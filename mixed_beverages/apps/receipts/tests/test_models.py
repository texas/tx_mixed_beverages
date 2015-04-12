from django.test import TestCase

from ..factories import LocationFactory, ReceiptFactory


class LocationTests(TestCase):
    def test_address_prop_works(self):
        location = LocationFactory()
        ReceiptFactory(
            address='123 Fake St',
            city='Brown Town',
            state='TX',
            zip='77777',
            location=location,
        )
        self.assertTrue(location.address)

    def test_address_props_with_no_latest(self):
        # TODO
        pass
