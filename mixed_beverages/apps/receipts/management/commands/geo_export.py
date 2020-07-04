from django.core.management.base import BaseCommand
from csv import DictWriter

from mixed_beverages.apps.receipts.models import Location


class Command(BaseCommand):
    help = """
    Helper to make a CSV for batch geocoding. See https://www.geocod.io/guides/preparing-your-spreadsheet/

    Then upload it to https://dash.geocod.io/import
    """

    def add_arguments(self, parser):
        parser.add_argument(
            "--limit", type=int, help="Only export up to this many locations"
        )

    def handle(self, limit, *args, **options):
        fieldnames = ("street_address", "city", "state", "zip", "pk")
        qs = Location.objects.filter(
            coordinate__isnull=True, zip__startswith="78"
        ).values(*fieldnames)
        if limit is not None:
            qs = qs[:limit]

        print(f"Exporting {qs.count()} locations...")
        with open("geo_export.csv", "w", newline="") as csvfile:
            writer = DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in qs:
                writer.writerow(row)
