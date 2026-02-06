import os.path
from csv import DictReader

from django.contrib.gis.geos import Point
from django.core.management.base import BaseCommand
from tqdm import tqdm

from mixed_beverages.apps.receipts.models import Location


class Command(BaseCommand):
    help = (
        "Import batch geocoding results from Geocodio. Overwrites existing coordinates."
    )

    def add_arguments(self, parser):
        parser.add_argument("csv")
        parser.add_argument(
            "--ignore-pk", action="store_true", help='ignore "pk" field of csv'
        )

    def handle(self, csv: str, ignore_pk: bool, *args, **options):
        assert os.path.isfile(csv)

        with open(csv) as fh:
            row_count = sum(1 for row in fh)
            fh.seek(0)
            reader = DictReader(fh)
            for row in tqdm(reader, total=row_count - 1):
                try:
                    if ignore_pk:
                        location = Location.objects.get(
                            street_address=row["street_address"],
                            city=row["city"],
                            state=row["state"],
                            zip=row["zip"],
                        )
                    else:
                        location = Location.objects.get(pk=row["pk"])
                except Exception:
                    continue
                # Handle both old and new Geocodio export formats
                longitude = row.get("Geocodio Longitude") or row.get("Longitude")
                latitude = row.get("Geocodio Latitude") or row.get("Latitude")
                accuracy_score = row.get("Geocodio Accuracy Score") or row.get(
                    "Accuracy Score"
                )

                if longitude and latitude:
                    location.coordinate = Point(x=float(longitude), y=float(latitude))
                    location.coordinate_quality = accuracy_score
                    location.save()
