import json

from django.test import TestCase
from unittest.mock import patch

from ..factories import LocationFactory, ReceiptFactory


# See https://github.com/crccheck/geodude#example
OK_GEODUDE_RESPONSE = json.loads("""
{
  "geometry": {
    "coordinates": [
      "-97.740133410666",
      "30.2754538274838"
    ],
    "type": "Point"
  },
  "properties": {
    "timestamp": "2016-12-03T03:42:37.605378Z",
    "quality": "03"
  },
  "type": "Feature"
}
""")


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

    @patch('mixed_beverages.apps.receipts.models.geocode_address')
    def test_geocode_does_nothing_when_no_receipts(self, mock_geocode_address):
        location = LocationFactory()
        self.assertFalse(location.receipts.all().exists())  # sanity check
        self.assertFalse(mock_geocode_address.called)

    @patch('mixed_beverages.apps.receipts.models.geocode_address')
    def test_geocode_geocodes(self, mock_geocode_address):
        mock_geocode_address.return_value = OK_GEODUDE_RESPONSE
        location = LocationFactory(receipts=[ReceiptFactory()])

        location.geocode()

        self.assertEqual(location.coordinate.x, -97.740133410666)
