import logging

from django.db import models
from django.contrib.gis.geos import Point
from django.contrib.postgres.fields import JSONField
from django.urls import reverse

from mixed_beverages.apps.lazy_geo.models import BaseLocation
from mixed_beverages.apps.lazy_geo.utils import geocode_address


class Business(models.Model):
    name = models.CharField(max_length=100)
    tax_number = models.CharField(max_length=50, primary_key=True)

    class Meta:
        verbose_name_plural = "businesses"

    def __str__(self):
        return self.name


class Location(BaseLocation):
    name = models.CharField(
        max_length=100, help_text="Location name from one of the receipts"
    )
    street_address = models.CharField(max_length=100)
    city = models.CharField(max_length=30)
    state = models.CharField(max_length=20)
    zip = models.CharField(max_length=15)

    data = JSONField(
        null=True, blank=True, help_text="denormalized data to help generate map data"
    )

    def __str__(self):
        bits = []
        if self.name:
            bits.append(self.name)
        if self.coordinate_quality:
            bits.append("({0.y},{0.x})".format(self.coordinate))
            bits.append(self.coordinate_quality)
        return " ".join(bits)

    def get_absolute_url(self):
        return "{0}#16/{1.coordinate.y}/{1.coordinate.x}".format(
            reverse("mixed_beverages:home"), self
        )

    @property
    def address(self):
        return f"{self.street_address}\n{self.city}, {self.state} {self.zip}"

    def geocode(self, force=False):
        logger = logging.getLogger("geocode")
        if self.coordinate and not force:
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
        self.coordinate = Point(x=float(data["Longitude"]), y=float(data["Latitude"]),)
        self.coordinate_quality = data["NAACCRGISCoordinateQualityCode"]
        self.save()
        logger.debug(data)
        logger.info("%s", self)


class Receipt(models.Model):
    """
    A location's tax receipt for a month

    $ csvstat Mixed_Beverage_Gross_Receipts.csv --len
    1. Taxpayer Number: None
    2. Taxpayer Name: 50
    3. Taxpayer Address: 40
    4. Taxpayer City: 20
    5. Taxpayer State: 2
    6. Taxpayer Zip: None
    7. Taxpayer County: None
    8. Location Number: None
    9. Location Name: 50
    10. Location Address: 50
    11. Location City: 23
    12. Location State: 2
    13. Location Zip: None
    14. Location County: None
    15. Inside/Outside City Limits: None
    16. TABC Permit Number: 12
    17. Responsibility Begin Date: None
    18. Responsibility End Date: None
    19. Obligation End Date: None
    20. Liquor Receipts: None
    21. Wine Receipts: None
    22. Beer Receipts: None
    23. Cover Charge Receipts: None
    24. Total Receipts: None
    """

    taxpayer_name = models.CharField(max_length=100)
    # TODO figure out name/tax_numbner/tabc_permit cardinality
    tax_number = models.CharField("taxpayer number", max_length=80)
    tabc_permit = models.CharField(
        "TABC permit number", max_length=40, help_text="example: MB888888"
    )
    # responsibility begin date
    # responsibility end date
    date = models.DateField(help_text="Obligation End Date")
    # taxpayer address, city, zip, county

    liquor = models.DecimalField("liquor receipts", max_digits=13, decimal_places=2)
    wine = models.DecimalField("wine receipts", max_digits=13, decimal_places=2)
    beer = models.DecimalField("beer receipts", max_digits=13, decimal_places=2)
    cover = models.DecimalField(
        "cover charge receipts", max_digits=13, decimal_places=2
    )
    # NOTE: total isn't always the sum. See LEGGER COCKTAILS
    total = models.DecimalField("total receipts", max_digits=13, decimal_places=2)
    # location fields
    location_name = models.CharField(max_length=100)
    location_number = models.PositiveSmallIntegerField()
    county_code = models.PositiveSmallIntegerField(help_text="A number from 1 to 254")
    # inside/outside city limits

    # Denormalized fields, populated in after import
    business = models.ForeignKey(
        Business,
        related_name="receipts",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    location = models.ForeignKey(
        Location,
        related_name="receipts",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ("-date",)
        unique_together = ("tabc_permit", "date")

    def __str__(self):
        return f"{self.location_name} {self.date} {self.total}"

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
