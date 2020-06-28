from __future__ import unicode_literals

import factory
from django.contrib.gis.geos import Point


from . import models
from ..receipts.factories import LocationFactory


class CorrectionFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Correction

    to = factory.LazyAttribute(lambda x: Point(0, 1))
    fro = factory.LazyAttribute(lambda x: Point(2, 3))
    obj = factory.SubFactory(LocationFactory)
