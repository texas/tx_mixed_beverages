from django.test import TestCase

from ..factories import LocationFactory, ReceiptFactory
from ..models import Location
from ..utils import group_by_location, set_location_data


def refresh(instance):
    return instance._meta.model.objects.get(pk=instance.pk)


class PostProcessTests(TestCase):
    def test_group_by_location_works(self):
        # sanity check
        self.assertFalse(Location.objects.all().exists())

        r1 = ReceiptFactory(location=None)
        r2 = ReceiptFactory(
            address=r1.address, city=r1.city, state=r1.state, zip=r1.zip, location=None
        )
        r3 = ReceiptFactory(location=None)

        # between 1 and 1 + 3n queries
        with self.assertNumQueries(7):
            group_by_location()
        r1 = refresh(r1)
        r2 = refresh(r2)
        r3 = refresh(r3)
        self.assertTrue(r1.location)
        self.assertTrue(r3.location)
        self.assertEqual(r1.location, r2.location)
        self.assertNotEqual(r3.location, r1.location)
        self.assertEqual(Location.objects.count(), 2)

    def test_set_location_data_filters_old_avg_tax(self):
        # setup
        location = LocationFactory()
        ReceiptFactory(location=location, date="1970-11-01", total=1)
        # need a recent receipt so it knows not to go back in time
        ReceiptFactory(date="2015-02-01", total=1337)

        set_location_data()

        location = Location.objects.get(pk=location.pk)
        self.assertEqual(location.data["avg_tax"], "0")

    def test_set_location_data_deletes_old_data(self):
        # setup
        location = LocationFactory()
        receipt = ReceiptFactory(location=location, date="2015-02-01", total=1)
        # need a recent receipt so it knows not to go back in time
        ReceiptFactory(date="2015-02-01", total=1337)

        set_location_data()
        location.refresh_from_db()
        # sanity check
        self.assertEqual(location.data["avg_tax"], "1.00")

        receipt.date = "1970-01-01"
        receipt.save()
        set_location_data()

        location.refresh_from_db()
        self.assertEqual(location.data["avg_tax"], "0")  # not NULL like above

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
        self.assertEqual(float(location.data["avg_tax"]), 3.5)

    def test_set_location_data_only_has_two_decimal_places(self):
        # setup
        location = LocationFactory()
        ReceiptFactory(location=location, date="2015-01-01", total=3.3333333333)

        set_location_data()

        location = Location.objects.get(pk=location.pk)
        self.assertEqual(float(location.data["avg_tax"]), 3.33)
