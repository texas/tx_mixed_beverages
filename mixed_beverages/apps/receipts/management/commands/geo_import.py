import os.path

from csv import DictReader
from django.contrib.gis.geos import Point
from django.core.management.base import BaseCommand
from obj_update import obj_update_or_create
from tqdm import tqdm

from mixed_beverages.apps.receipts.models import Location


class Command(BaseCommand):
    help = "Import batch geocoding results from Geocodio"

    def add_arguments(self, parser):
        parser.add_argument("csv")

    def handle(self, csv, *args, **options):
        assert os.path.isfile(csv)

        with open(csv, "r") as fh:
            row_count = sum(1 for row in fh)
            fh.seek(0)
            reader = DictReader(fh)
            for row in tqdm(reader, total=row_count - 1):
                # TODO can I add `pk` to the row to simplify this query?
                location = Location.objects.get(
                    street_address=row["street_address"],
                    city=row["city"],
                    state=row["state"],
                    zip=row["zip"],
                )
                location.coordinate = Point(
                    x=float(row["Longitude"]), y=float(row["Latitude"])
                )
                # TODO turn row['Accuracy Score'] into location.coordinate_quality
                location.save()
                # print(location, row)
