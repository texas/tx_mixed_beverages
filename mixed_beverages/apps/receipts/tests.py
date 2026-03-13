from unittest.mock import MagicMock

from django.test import TestCase

from .management.commands.slurp import deduplicate_receipts
from .management.commands.slurp_api import import_data_from_api
from .models import Receipt


def make_receipt(tabc_permit, tax_number, date, location_number):
    r = MagicMock()
    r.tabc_permit = tabc_permit
    r.tax_number = tax_number
    r.date = date
    r.location_number = location_number
    return r


class DeduplicateReceiptsTest(TestCase):
    def test_same_tax_number_keeps_lowest_location_number(self):
        venue = make_receipt("TB015938", "111", "2007-10-31", "1")
        event = make_receipt("TB015938", "111", "2007-10-31", "3")

        result = deduplicate_receipts([venue, event])

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].location_number, "1")

    def test_same_tax_number_keeps_lowest_location_number_regardless_of_order(self):
        event = make_receipt("TB015938", "111", "2007-10-31", "3")
        venue = make_receipt("TB015938", "111", "2007-10-31", "1")

        result = deduplicate_receipts([event, venue])

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].location_number, "1")

    def test_different_tax_numbers_keeps_both_ownership_change_records(self):
        old_owner = make_receipt("MB200114651", "32062684942", "2026-01-31", "1")
        new_owner = make_receipt("MB200114651", "32103027788", "2026-01-31", "1")

        result = deduplicate_receipts([old_owner, new_owner])

        self.assertEqual(len(result), 2)
        tax_numbers = {r.tax_number for r in result}
        self.assertEqual(tax_numbers, {"32062684942", "32103027788"})


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
