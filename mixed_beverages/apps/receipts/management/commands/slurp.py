import os.path
import csv as csv_lib

from django.core.management.base import BaseCommand
from obj_update import obj_update_or_create
from tqdm import tqdm

from ...models import Location, Receipt


def date_fmt(date: str):
    """Convert m/d/y to Y-M-D"""
    try:
        month, day, year = date.split("/")
        return f"{year}-{month}-{day}"

    except:
        return None


class Command(BaseCommand):
    help = "Import a CSV file. Doing a full import over 2.3MM rows will take about 1.5 hours"

    def add_arguments(self, parser):
        parser.add_argument("csv")

    def handle(self, csv, *args, **options):
        assert os.path.isfile(csv)

        with open(csv, "r", encoding="windows-1252") as fh:
            row_count = sum(1 for row in fh) - 1
            fh.seek(0)
            reader = csv_lib.DictReader(fh)
            for row in tqdm(reader, total=row_count):
                location, __ = Location.objects.get_or_create(
                    street_address=row["Location Address"],
                    city=row["Location City"],
                    state=row["Location State"],
                    zip=row["Location Zip"],
                    defaults=dict(data={"name": row["Location Name"]}),
                )
                receipt, created = obj_update_or_create(
                    Receipt,
                    tax_number=row["Taxpayer Number"],
                    date=date_fmt(row["Obligation End Date"]),
                    defaults=dict(
                        name=row["Taxpayer Name"],
                        tabc_permit=row["TABC Permit Number"],
                        liquor=row["Liquor Receipts"],
                        wine=row["Wine Receipts"],
                        beer=row["Beer Receipts"],
                        cover=row["Cover Charge Receipts"],
                        total=row["Total Receipts"],
                        location_name=row["Location Name"],
                        location_number=row["Location Number"],
                        county_code=row["Location County"],
                        location=location,
                    ),
                )
