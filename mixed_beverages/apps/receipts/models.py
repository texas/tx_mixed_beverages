import logging

from django.db import models
from django.contrib.gis.geos import Point
from django.contrib.postgres.fields import JSONField
from django.urls import reverse

from mixed_beverages.apps.lazy_geo.models import BaseLocation
from mixed_beverages.apps.lazy_geo.utils import geocode_address


class Business(models.Model):
    name = models.CharField(max_length=30)

    class Meta:
        verbose_name_plural = "businesses"

    def __str__(self):
        return self.name


class Location(BaseLocation):
    data = JSONField(
        null=True, blank=True, help_text="denormalized data to help generate map data"
    )
    businesses = models.ManyToManyField(related_name="locations")

    def __str__(self):
        bits = []
        if self.data:
            bits.append(self.data["name"])
        if self.coordinate_quality:
            bits.append("({0.y},{0.x})".format(self.coordinate))
            bits.append(self.coordinate_quality)
        return " ".join(bits)

    def get_absolute_url(self):
        return "{0}#16/{1.coordinate.y}/{1.coordinate.x}".format(
            reverse("mixed_beverages:home"), self
        )

    # CUSTOM PROPERTIES #
    @property
    def address(self):
        """Get a human readable address."""
        latest = self.get_latest()
        if not latest:
            return ""

        return "{0.address}\n{0.city}, {0.state} {0.zip}".format(latest)

    # CUSTOM METHODS #

    def get_latest(self):
        try:
            return self.receipts.order_by("-date")[0]
        except IndexError:
            return None

    def geocode(self, force=False):
        logger = logging.getLogger("geocode")
        if self.coordinate and not force:
            logger.info("{} already geocoded".format(self))
            return

        receipt = self.get_latest()
        if receipt is None:
            logger.warning("Location {} has no address".format(self.pk))
            return

        data = geocode_address(
            {
                "address": receipt.address,
                "city": receipt.city,
                "state": receipt.state,
                "zipcode": receipt.zip,
            }
        )
        self.coordinate = Point(x=float(data["Longitude"]), y=float(data["Latitude"]),)
        self.coordinate_quality = data["NAACCRGISCoordinateQualityCode"]
        self.save()
        logger.debug(data)
        logger.info("%s", self)


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
    date = models.DateField(help_text="Use the 1st of the month for simplicity")
    tax = models.DecimalField(max_digits=13, decimal_places=2)
    # location fields
    address = models.CharField(max_length=30)
    city = models.CharField(max_length=20)
    state = models.CharField(max_length=2)
    zip = models.CharField(max_length=5)
    county_code = models.PositiveSmallIntegerField()

    # bookkeeping
    source = models.CharField(max_length=255, null=True, blank=True)

    # denormalized fields
    business = models.ForeignKey(
        Business,
        related_name="receipts",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    location = models.ForeignKey(
        Location,
        related_name="receipts",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ("-date",)

    def __str__(self):
        return "{} {} {}".format(self.name, self.date, self.tax)

    # CUSTOM METHODS #

    def geocode(self, force=False):
        logger = logging.getLogger("geocode")
        location = self.location
        if location and location.coordinate and not force:
            logger.info("{} already geocoded".format(self))
            return

        data = geocode_address(
            {
                "address": self.address,
                "city": self.city,
                "state": self.state,
                "zipcode": self.zip,
            }
        )
        location.coordinate = Point(
            x=float(data["Longitude"]), y=float(data["Latitude"]),
        )
        location.coordinate_quality = data["NAACCRGISCoordinateQualityCode"]
        location.save()
        logger.debug(data)
        logger.info("{}".format(location))
