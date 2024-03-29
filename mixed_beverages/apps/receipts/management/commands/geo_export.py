from django.core.management.base import BaseCommand
from csv import DictWriter

from mixed_beverages.apps.receipts.models import Location


class Command(BaseCommand):
    help = """
    Helper to make a CSV for batch geocoding. Writes to "geo_export.csv"
    See https://www.geocod.io/guides/preparing-your-spreadsheet/
    """

    def add_arguments(self, parser):
        parser.add_argument(
            "--limit",
            type=int,
            default=2500,
            help="Only export up to this many locations (default: 2500)",
        )

    def handle(self, limit, *args, **options):
        fieldnames = ("street_address", "city", "state", "zip", "pk")
        qs = Location.objects.filter(coordinate__isnull=True).values(*fieldnames)
        original_count = qs.count()
        if limit is not None:
            qs = qs[:limit]

        self.stdout.write(
            f"Exporting {qs.count()} out of {original_count} locations..."
        )
        with open("geo_export.csv", "w", newline="") as csvfile:
            writer = DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in qs:
                writer.writerow(row)
        self.stdout.write("Now upload geo_export.csv at https://dash.geocod.io/import")
