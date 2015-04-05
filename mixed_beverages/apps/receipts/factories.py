from __future__ import unicode_literals

from datetime import date
import string

import factory
from factory.fuzzy import FuzzyDate, FuzzyDecimal, FuzzyText

from . import models


class LocationFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Location


class ReceiptFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Receipt

    tabc_permit = FuzzyText(length=6, prefix='MB', chars=string.digits)
    name = FuzzyText(length=30)
    date = FuzzyDate(start_date=date(1970, 1, 1))
    tax = FuzzyDecimal(low=0, high=10000, precision=2)
    address = FuzzyText(length=30)
    city = FuzzyText(length=20)
    state = FuzzyText(length=2)
    zip = FuzzyText(length=5, chars=string.digits)
    county_code = 1337

    location = factory.SubFactory(LocationFactory)
