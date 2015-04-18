# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.contrib.gis.db import models
from django.contrib.gis.geos import Point
from django.core.exceptions import SuspiciousOperation
from django.utils import timezone


class BaseLocation(models.Model):
    # http://geoservices.tamu.edu/Services/Geocode/About/#NAACCRGISCoordinateQualityCodes
    QUALITY_CHOICES = (
        ('me', 'User Inputted'),
        ('00', 'AddressPoint'),
        # 'Coordinates derived from local government-maintained address '
        # 'points, which are based on property parcel locations, not '
        # 'interpolation over a street segment’s address range')
        ('01', 'GPS'),
        # 'Coordinates assigned by Global Positioning System (GPS)')
        ('02', 'Parcel'),
        # 'Coordinates are match of house number and '
        # 'street, and based on property parcel location')
        ('03', 'StreetSegmentInterpolation'),
        # 'Coordinates are match '
        #   'of house number and street, interpolated over the matching '
        #   'street segment’s address range')
        ('09', 'AddressZipCentroid'),
        # 'Coordinates are address 5-digit ZIP code centroid')
        ('10', 'POBoxZIPCentroid'),
        # 'Coordinates are point ZIP code '
        # 'of Post Office Box or Rural Route')
        ('11', 'CityCentroid'),
        # 'Coordinates are centroid of address '
        # 'city (when address ZIP code is unknown or invalid, and there are '
        # 'multiple ZIP codes for the city)')
        ('98', 'Unknown'),
        # 'Latitude and longitude are assigned, but '
        # 'coordinate quality is unknown')
        ('99', 'Unmatchable'),
        # 'Latitude and longitude are not '
        # 'assigned, but geocoding was attempted; unable to assign '
        # 'coordinates based on available information')
    )

    coordinate = models.PointField(null=True, blank=True)
    coordinate_quality = models.CharField(max_length=2,
        choices=QUALITY_CHOICES, null=True, blank=True)

    # MANAGERS #
    objects = models.GeoManager()

    class Meta:
        abstract = True

    def __unicode__(self):
        return unicode(self.coordinate or self.pk)

    # CUSTOM METHODS #

    def geocode(self, force=False):
        # TODO raise NotImplementedError
        pass


class CorrectionManager(models.GeoManager):
    def create_from_request(self, obj, request):
        lat = request.POST.get('lat')
        lng = request.POST.get('lng')
        data = {}
        if request.user.is_anonymous():
            if settings.ALLOW_ANONYMOUS_CORRECTIONS:
                data['submitter'] = None
            else:
                raise SuspiciousOperation('must be logged in')
        else:
            data['submitter'] = request.user
        if lat and lng:
            data.update(
                fro=obj.coordinate,
                to=Point(
                    x=float(lng),
                    y=float(lat),
                ),
                approved=False,
                status='submitted',
                obj=obj,
                ip_address=request.META.get('HTTP_X_FORWARDED_FOR',
                    request.META.get('REMOTE_ADDR')),
            )
        else:
            # TODO better exception
            raise TypeError('missing lat or lng')
        return self.create(**data)


class Correction(models.Model):
    """
    A user submitted coordinate correction.

    WISHLIST have a state for reject, revert

    Some inspiration from django.contrib.comments:
    https://github.com/django/django-contrib-comments/blob/master/django_comments/models.py
    """
    STATUS_CHOICES = (
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )

    fro = models.PointField(help_text='The old coordinate')
    to = models.PointField(help_text='The suggested coordinate')
    approved = models.BooleanField(default=False)
    submitter = models.ForeignKey(settings.AUTH_USER_MODEL,
        related_name='+',
        null=True, blank=True)
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL,
        related_name='+',
        null=True, blank=True)
    # should be a GFK if we want to be generic
    obj = models.ForeignKey('receipts.Location')
    created_at = models.DateTimeField(default=timezone.now)
    approved_at = models.DateTimeField(null=True, blank=True)
    ip_address = models.GenericIPAddressField('IP address', unpack_ipv4=True,
        blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    comment = models.TextField(null=True, blank=True)

    obj_coordinate_field = 'coordinate'
    obj_coordinate_quality_field = 'coordinate_quality'

    # MANAGERS #
    objects = CorrectionManager()

    def __unicode__(self):
        return 'by {0.submitter}'.format(self)

    def approve(self, approver):
        setattr(self.obj, self.obj_coordinate_field, self.to)
        setattr(self.obj, self.obj_coordinate_quality_field, 'me')
        self.obj.save()
        self.approved_by = approver
        self.approved = True
        self.approved_at = timezone.now()
        self.status = 'approved'
        self.save()
