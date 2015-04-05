from django.test import TestCase

from ..factories import ReceiptFactory
from ..models import Location
from ..utils import row_to_receipt, group_by_location


def refresh(instance):
    return instance._meta.model.objects.get(pk=instance.pk)


class RowToReceiptTests(TestCase):
    def test_row_to_receipt_works(self):
        test_row = '"MB821424","ABI-HAUS                      ","959 N 2ND ST                  ","ABILENE             ","TX","79601","221","          ","2014/11", 000000963.19'
        row = test_row.replace('"', '').split(',')  # stupid csv logic
        receipt = row_to_receipt(row)
        self.assertEqual(receipt.name, 'ABI-HAUS')


class PostProcessTests(TestCase):
    def test_group_by_location_works(self):
        # sanity check
        self.assertFalse(Location.objects.all().exists())

        r1 = ReceiptFactory(location=None)
        r2 = ReceiptFactory(address=r1.address, city=r1.city, state=r1.state,
            zip=r1.zip, location=None)
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

    def test_set_location_data_works(self):
        pass
