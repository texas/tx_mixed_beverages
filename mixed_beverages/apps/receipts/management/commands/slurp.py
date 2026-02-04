import csv as csv_lib
import os.path
from functools import lru_cache

from django.core.management.base import BaseCommand
from obj_update import obj_update_or_create
from tqdm import tqdm

from ...models import Location, Receipt


def date_fmt(date: str):
    """Convert m/d/y to Y-M-D"""
    try:
        month, day, year = date.split("/")
        return f"{year}-{month}-{day}"

    except Exception:
        return None


@lru_cache(maxsize=512)
def location_get(street_address, city, state, zip_code, name):
    """
    Wrapper around Location.objects.get_or_create just to use lru_cache
    """
    location, __ = Location.objects.get_or_create(
        street_address=street_address,
        city=city,
        state=state,
        zip=zip_code,
        defaults={"name": name},
    )
    return location


class Command(BaseCommand):
    help = "Import a CSV file. Doing a full import over 2.4MM rows will take "
    "about 1.5 hours"

    def add_arguments(self, parser):
        parser.add_argument("csv")

    def handle(self, csv, *args, **options):
        assert os.path.isfile(csv)

        with open(csv, encoding="windows-1252") as fh:
            row_count = sum(1 for row in fh) - 1
            fh.seek(0)
            reader = csv_lib.DictReader(fh)
            for row in tqdm(reader, total=row_count):
                location = location_get(
                    street_address=row["Location Address"],
                    city=row["Location City"],
                    state=row["Location State"],
                    zip_code=row["Location Zip"],
                    name=row["Location Name"],
                )
                obj_update_or_create(
                    Receipt,
                    tabc_permit=row["TABC Permit Number"],
                    date=date_fmt(row["Obligation End Date"]),
                    defaults={
                        "taxpayer_name": row["Taxpayer Name"],
                        "tax_number": row["Taxpayer Number"],
                        "liquor": row["Liquor Receipts"],
                        "wine": row["Wine Receipts"],
                        "beer": row["Beer Receipts"],
                        "cover": row["Cover Charge Receipts"],
                        "total": row["Total Receipts"],
                        "location_name": row["Location Name"],
                        "location_number": row["Location Number"],
                        "county_code": row["Location County"],
                        "location": location,
                    },
                )
