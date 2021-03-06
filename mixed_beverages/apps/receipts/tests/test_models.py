from django.test import TestCase
from unittest.mock import patch

from ..factories import LocationFactory, ReceiptFactory


class LocationTests(TestCase):
    def test_address_prop_works(self):
        location = LocationFactory()
        self.assertTrue(location.address)

    @patch("mixed_beverages.apps.receipts.models.geocode_address")
    def test_geocode_does_nothing_when_no_receipts(self, mock_geocode_address):
        location = LocationFactory()
        self.assertFalse(location.receipts.all().exists())  # sanity check
        self.assertFalse(mock_geocode_address.called)

    @patch("mixed_beverages.apps.receipts.models.geocode_address")
    def test_geocode_geocodes(self, mock_geocode_address):
        mock_geocode_address.return_value = {
            "Longitude": "0.0",
            "Latitude": "0.0",
            "NAACCRGISCoordinateQualityCode": "98",
        }
        location = LocationFactory(receipts=[ReceiptFactory()])

        location.geocode()

        self.assertEqual(location.coordinate.x, 0.0)
