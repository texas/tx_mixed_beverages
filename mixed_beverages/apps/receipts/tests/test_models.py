from django.test import TestCase
from unittest.mock import patch

from ..factories import LocationFactory, ReceiptFactory


class LocationTests(TestCase):
    def test_address_prop_works(self):
        location = LocationFactory()
        self.assertTrue(location.address)
