from django.conf import settings
from django.contrib.gis.db import models
from django.contrib.gis.geos import Point
from django.core.exceptions import SuspiciousOperation
from django.urls import reverse
from django.utils import timezone


class BaseTAMULocation(models.Model):
    # http://geoservices.tamu.edu/Services/Geocode/About/#NAACCRGISCoordinateQualityCodes
    QUALITY_CHOICES = (
        ("me", "User Inputted"),
        ("00", "AddressPoint"),
        # 'Coordinates derived from local government-maintained address '
        # 'points, which are based on property parcel locations, not '
        # 'interpolation over a street segment’s address range')
        ("01", "GPS"),
        # 'Coordinates assigned by Global Positioning System (GPS)')
        ("02", "Parcel"),
        # 'Coordinates are match of house number and '
        # 'street, and based on property parcel location')
        ("03", "StreetSegmentInterpolation"),
        # 'Coordinates are match '
        #   'of house number and street, interpolated over the matching '
        #   'street segment’s address range')
        ("09", "AddressZipCentroid"),
        # 'Coordinates are address 5-digit ZIP code centroid')
        ("10", "POBoxZIPCentroid"),
        # 'Coordinates are point ZIP code '
        # 'of Post Office Box or Rural Route')
        ("11", "CityCentroid"),
        # 'Coordinates are centroid of address '
        # 'city (when address ZIP code is unknown or invalid, and there are '
        # 'multiple ZIP codes for the city)')
        ("98", "Unknown"),
        # 'Latitude and longitude are assigned, but '
        # 'coordinate quality is unknown')
        ("99", "Unmatchable"),
        # 'Latitude and longitude are not '
        # 'assigned, but geocoding was attempted; unable to assign '
        # 'coordinates based on available information')
    )

    coordinate = models.PointField(null=True, blank=True)
    coordinate_quality = models.CharField(
        max_length=2, choices=QUALITY_CHOICES, null=True, blank=True
    )

    class Meta:
        abstract = True

    def __str__(self):
        return str(self.coordinate or self.pk)


class BaseGeocodioLocation(models.Model):
    coordinate = models.PointField(null=True, blank=True)
    # https://www.geocod.io/guides/accuracy-types-scores/
    coordinate_quality = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="1 is most accuracy, 0.8 is pretty close, anything less than 0.6 is bad",
    )

    class Meta:
        abstract = True

    def __str__(self):
        return str(self.coordinate or self.pk)
