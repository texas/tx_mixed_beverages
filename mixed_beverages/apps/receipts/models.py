from django.db import models
from django.contrib.gis.db import models as geo_models


class Business(models.Model):
    """
    A business can have multiple locations.
    """
    name = models.CharField(max_length=30)


class Receipt(models.Model):
    """

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
    """
    permit = models.CharField(max_length=8)
    name = models.CharField(max_length=30)
    date = models.DateField()
    tax = models.DecimalField(max_digits=13, decimal_places=2)
    business = models.ForeignKey(Business)


class Location(geo_models.Model):
    """
    The location a reciept was paid.
    """
    address = models.CharField(max_length=30)
    city = models.CharField(max_length=20)
    state = models.CharField(max_length=2)
    zip = models.CharField(max_length=5)
    county_code = models.PositiveSmallIntegerField()
    coordinate = geo_models.PointField(null=True, blank=True)

    # MANAGERS #
    objects = geo_models.GeoManager()
