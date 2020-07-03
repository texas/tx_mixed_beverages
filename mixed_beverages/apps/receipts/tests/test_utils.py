from django.test import TestCase

from ..factories import LocationFactory, ReceiptFactory
from ..models import Location
from ..utils import set_location_data


def refresh(instance):
    return instance._meta.model.objects.get(pk=instance.pk)


class PostProcessTests(TestCase):
    def test_set_location_data_filters_old_avg_tax(self):
        # setup
        location = LocationFactory()
        ReceiptFactory(location=location, date="1970-11-01", total=1)
        # need a recent receipt so it knows not to go back in time
        ReceiptFactory(date="2015-02-01", total=1337)

        set_location_data()

        location = Location.objects.get(pk=location.pk)
        self.assertEqual(location.data["avg_total"], "0")

    def test_set_location_data_deletes_old_data(self):
        # setup
        location = LocationFactory()
        receipt = ReceiptFactory(location=location, date="2015-02-01", total=1)
        # need a recent receipt so it knows not to go back in time
        ReceiptFactory(date="2015-02-01", total=1337)

        set_location_data()
        location.refresh_from_db()
        # sanity check
        self.assertEqual(location.data["avg_total"], "1.00")

        receipt.date = "1970-01-01"
        receipt.save()
        set_location_data()

        location.refresh_from_db()
        self.assertEqual(location.data["avg_total"], "0")  # not NULL like above

    def test_set_location_data_works(self):
        # setup
        location = LocationFactory()
        ReceiptFactory(location=location, date="2014-11-01", total=1)
        ReceiptFactory(location=location, date="2014-12-01", total=2)
        ReceiptFactory(location=location, date="2015-01-01", total=3)
        ReceiptFactory(location=location, date="2015-02-01", total=4)
        ReceiptFactory(location=location, date="2015-03-01", total=5)

        set_location_data()

        location = Location.objects.get(pk=location.pk)
        self.assertEqual(float(location.data["avg_total"]), 3.0)

    def test_set_location_data_only_has_two_decimal_places(self):
        # setup
        location = LocationFactory()
        ReceiptFactory(location=location, date="2015-01-01", total=3.3333333333)

        set_location_data()

        location = Location.objects.get(pk=location.pk)
        self.assertEqual(float(location.data["avg_total"]), 3.33)
