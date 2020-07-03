from django.core.management.base import BaseCommand
from csv import DictWriter

from mixed_beverages.apps.receipts.models import Location


class Command(BaseCommand):
    help = """
    Helper to make a CSV for batch geocoding. See https://www.geocod.io/guides/preparing-your-spreadsheet/

    Then upload it to https://dash.geocod.io/import
    """

    def handle(self, *args, **options):
        fieldnames = ("street_address", "city", "state", "zip")
        qs = Location.objects.filter(zip__startswith="787").values(*fieldnames)

        with open("geo_export.csv", "w", newline="") as csvfile:
            writer = DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in qs:
                writer.writerow(row)