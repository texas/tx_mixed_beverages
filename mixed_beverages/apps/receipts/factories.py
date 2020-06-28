from __future__ import unicode_literals

from datetime import date
import string

import factory
from factory.fuzzy import FuzzyDate, FuzzyDecimal, FuzzyText

from . import models


class LocationFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Location

    @factory.post_generation
    def receipts(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for receipt in extracted:
                self.receipts.add(receipt)


class ReceiptFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Receipt

    tax_number = factory.Faker("pyint")
    tabc_permit = FuzzyText(length=6, prefix="MB", chars=string.digits)
    name = FuzzyText(length=30)
    date = FuzzyDate(start_date=date(1970, 1, 1))
    liquor = FuzzyDecimal(low=0, high=1000, precision=2)
    beer = FuzzyDecimal(low=0, high=1000, precision=2)
    wine = FuzzyDecimal(low=0, high=1000, precision=2)
    cover = FuzzyDecimal(low=0, high=1000, precision=2)
    total = FuzzyDecimal(low=0, high=10000, precision=2)
    location_number = 1
    address = factory.Faker("street_address")
    city = factory.Faker("city")
    state = "TX"
    zip = FuzzyText(length=5, chars=string.digits)
    county_code = 255

    location = factory.SubFactory(LocationFactory)
