# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.contrib.gis.db import models
from django.contrib.gis.geos import Point


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
        if lat and lng:
            return self.create(
                fro=obj.coordinate,
                to=Point(
                    x=float(lng),
                    y=float(lat),
                ),
                submitter=request.user,
                approved=False,
                obj=obj,
            )
        else:
            # TODO better exception
            raise Exception('bad input data')


class Correction(models.Model):
    """
    A user submitted coordinate correction.
    """
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

    obj_coordinate_field = 'coordinate'
    obj_coordinate_quality_field = 'coordinate_quality'

    # MANAGERS #
    objects = CorrectionManager()

    def approve(self, approver):
        setattr(self.obj, self.obj_coordinate_field, self.to)
        setattr(self.obj, self.obj_coordinate_quality_field, 'me')
        self.approved_by = approver
        self.obj.save()
