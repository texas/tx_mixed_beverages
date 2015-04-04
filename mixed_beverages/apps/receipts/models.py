# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging

from django.db import models
from django.contrib.gis.db import models as geo_models
from django.contrib.gis.geos import Point

from mixed_beverages.apps.lazy_geo.utils import geocode_address


class Business(models.Model):
    """
    A business can have multiple locations.
    """
    name = models.CharField(max_length=30)

    class Meta:
        verbose_name_plural = 'businesses'

    def __unicode__(self):
        return self.name

    @property
    def locations(self):
        return Location.objects.filter(receipts__business=self)


class Location(geo_models.Model):
    # http://geoservices.tamu.edu/Services/Geocode/About/#NAACCRGISCoordinateQualityCodes
    QUALITY_CHOICES = (
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

    coordinate = geo_models.PointField(null=True, blank=True)
    coordinate_quality = models.CharField(max_length=2,
        choices=QUALITY_CHOICES, null=True, blank=True)

    # MANAGERS #
    objects = geo_models.GeoManager()

    def __unicode__(self):
        return unicode(self.coordinate or self.pk)

    #

    def get_latest(self):
        try:
            return self.receipts.order_by('-date')[0]
        except IndexError:
            return None

    # CUSTOM METHODS #

    def geocode(self, force=False):
        logger = logging.getLogger('geocode')
        if self.coordinate and not force:
            logger.info('{} already geocoded'.format(self))
            return
        receipt = self.receipts.all()[0]
        data = geocode_address({
            'address': receipt.address,
            'city': receipt.city,
            'state': receipt.state,
            'zipcode': receipt.zip,
        })
        self.coordinate = Point(
            x=float(data['Longitude']),
            y=float(data['Latitude']),
        )
        self.coordinate_quality = data['NAACCRGISCoordinateQualityCode']
        self.save()
        logger.debug(data)
        logger.info('{}'.format(self))


class Receipt(models.Model):
    """
    A location's tax receipt for a month

    Column_Order|Column_Description|Data_Type|Size
    Col01|TABC Permit Number|Number|8
    Col02|Trade Name|Char|30
    Col03|Location Address|Char|30
    Col04|Locaiton City|Char|20
    Col05|Location State|Char|2
    Col06|Location Zip Code|Number|5
    Col07|Location County Code|Number|3
    Col08|Report Period (YYYY/MM)|Char|7
    Col09|Report Tax|Number|13

    Location fields maybe should get split out, but will make importing slower.
    """
    tabc_permit = models.CharField(max_length=8)
    name = models.CharField(max_length=30)
    date = models.DateField(
        help_text='Use the 1st of the month for simplicity')
    tax = models.DecimalField(max_digits=13, decimal_places=2)
    # location fields
    address = models.CharField(max_length=30)
    city = models.CharField(max_length=20)
    state = models.CharField(max_length=2)
    zip = models.CharField(max_length=5)
    county_code = models.PositiveSmallIntegerField()

    # denormalized fields
    business = models.ForeignKey(Business, related_name='receipts',
        null=True, blank=True)
    location = models.ForeignKey(Location, related_name='receipts',
        null=True, blank=True)

    def __unicode__(self):
        return '{} {} {}'.format(
            self.name,
            self.date,
            self.tax,
        )

    class Meta:
        ordering = ('-date', )

    # CUSTOM METHODS #

    def geocode(self, force=False):
        logger = logging.getLogger('geocode')
        location = self.location
        if location and location.coordinate and not force:
            logger.info('{} already geocoded'.format(self))
            return
        data = geocode_address({
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'zipcode': self.zip,
        })
        location.coordinate = Point(
            x=float(data['Longitude']),
            y=float(data['Latitude']),
        )
        location.coordinate_quality = data['NAACCRGISCoordinateQualityCode']
        location.save()
        logger.debug(data)
        logger.info('{}'.format(location))
