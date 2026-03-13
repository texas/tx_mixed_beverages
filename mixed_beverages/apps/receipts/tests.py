from django.test import TestCase

from .management.commands.slurp_api import import_data_from_api
from .models import Receipt

IMPERO_OLD = {
    "taxpayer_number": "32062684942",
    "taxpayer_name": "IMPERO ITALIANO INC.",
    "taxpayer_address": "14028 MEMORIAL DR",
    "taxpayer_city": "HOUSTON",
    "taxpayer_state": "TX",
    "taxpayer_zip": "77079",
    "taxpayer_county": "101",
    "location_number": "1",
    "location_name": "IMPERO ITALIANO",
    "location_address": "14028 MEMORIAL DR",
    "location_city": "HOUSTON",
    "location_state": "TX",
    "location_zip": "77079",
    "location_county": "101",
    "inside_outside_city_limits_code_y_n": "Y",
    "tabc_permit_number": "MB200114651",
    "responsibility_begin_date_yyyymmdd": "2023-11-20T00:00:00.000",
    "responsibility_end_date_yyyymmdd": "2026-01-21T00:00:00.000",
    "obligation_end_date_yyyymmdd": "2026-01-31T00:00:00.000",
    "liquor_receipts": "0",
    "wine_receipts": "0",
    "beer_receipts": "0",
    "cover_charge_receipts": "0",
    "total_receipts": "0",
}

IMPERO_NEW = {
    "taxpayer_number": "32103027788",
    "taxpayer_name": "IMPERO ITALIANO RISTORANTE & ARTISAN PIZZERIA LLC",
    "taxpayer_address": "14028 MEMORIAL DR",
    "taxpayer_city": "HOUSTON",
    "taxpayer_state": "TX",
    "taxpayer_zip": "77079",
    "taxpayer_county": "101",
    "location_number": "1",
    "location_name": "IMPERO ITALIANO RISTORANTE & ARTISAN PIZZERIA LLC",
    "location_address": "14028 MEMORIAL DR",
    "location_city": "HOUSTON",
    "location_state": "TX",
    "location_zip": "77079",
    "location_county": "101",
    "inside_outside_city_limits_code_y_n": "Y",
    "tabc_permit_number": "MB200114651",
    "responsibility_begin_date_yyyymmdd": "2026-01-22T00:00:00.000",
    "obligation_end_date_yyyymmdd": "2026-01-31T00:00:00.000",
    "liquor_receipts": "0",
    "wine_receipts": "0",
    "beer_receipts": "0",
    "cover_charge_receipts": "0",
    "total_receipts": "44776",
}


class ImportDataFromApiTest(TestCase):
    def test_same_permit_ownership_change_creates_two_receipts(self):
        import_data_from_api([IMPERO_OLD, IMPERO_NEW])

        receipts = Receipt.objects.filter(tabc_permit="MB200114651").order_by(
            "tax_number"
        )
        self.assertEqual(receipts.count(), 2)
        self.assertEqual(receipts[0].tax_number, "32062684942")
        self.assertEqual(receipts[1].tax_number, "32103027788")

    def test_same_permit_ownership_change_no_updates_on_reimport(self):
        import_data_from_api([IMPERO_OLD, IMPERO_NEW])

        created, updated = import_data_from_api([IMPERO_OLD, IMPERO_NEW])

        self.assertEqual(created, 0)
        self.assertEqual(updated, 0)
