from django.test import TestCase

from .slurp_api import import_data_from_api


class SlurpApiTests(TestCase):
    def test_trivial_nothing_happens_with_no_data(self):
        created_count = import_data_from_api([])
        self.assertEqual(created_count, 0)

    def test_import_works(self):
        # https://data.texas.gov/resource/naix-2893.json?$limit=1
        data = [
            {
                "taxpayer_number": "32047970895",
                "taxpayer_name": "HONDURAS MAYA CAFE & BAR LLC",
                "taxpayer_address": "8011 HAZEN ST",
                "taxpayer_city": "HOUSTON",
                "taxpayer_state": "TX",
                "taxpayer_zip": "77036",
                "taxpayer_county": "101",
                "location_number": "1",
                "location_name": "HONDURAS MAYA CAFE & BAR LLC",
                "location_address": "5945 BELLAIRE BLVD STE B",
                "location_city": "HOUSTON",
                "location_state": "TX",
                "location_zip": "77081",
                "location_county": "101",
                "inside_outside_city_limits_code_y_n": "Y",
                "tabc_permit_number": "MB817033",
                "responsibility_begin_date_yyyymmdd": "2012-08-16T00:00:00.000",
                "responsibility_end_date_yyyymmdd": "2019-09-12T00:00:00.000",
                "obligation_end_date_yyyymmdd": "2019-07-31T00:00:00.000",
                "liquor_receipts": "0",
                "wine_receipts": "0",
                "beer_receipts": "0",
                "cover_charge_receipts": "0",
                "total_receipts": "0",
            }
        ]
        created_count = import_data_from_api(data)
        self.assertEqual(created_count, 1)
