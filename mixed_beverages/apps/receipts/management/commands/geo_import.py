import os.path

from csv import DictReader
from django.contrib.gis.geos import Point
from django.core.management.base import BaseCommand
from obj_update import obj_update_or_create
from tqdm import tqdm

from mixed_beverages.apps.receipts.models import Location


def get_coordinate_quality(accuracy: str) -> str:
    # https://www.geocod.io/guides/accuracy-types-scores/
    if accuracy == "1":
        return "00"

    accuracy_value = float(accuracy)
    if accuracy_value > 0.8:
        return "01"

    return "98"


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

        with open(csv, "r") as fh:
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
                except:
                    continue
                location.coordinate = Point(
                    x=float(row["Longitude"]), y=float(row["Latitude"])
                )
                location.coordinate_quality = get_coordinate_quality(
                    row["Accuracy Score"]
                )
                location.save()
