from django.test import TestCase

from ..factories import LocationFactory


class LocationTests(TestCase):
    def test_address_prop_works(self):
        location = LocationFactory()
        self.assertTrue(location.address)
