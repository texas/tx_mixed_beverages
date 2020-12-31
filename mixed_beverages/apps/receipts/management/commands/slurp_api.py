import os.path
from functools import lru_cache
import requests

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


@lru_cache(maxsize=512)
def Location_get(street_address, city, state, zip, name):
    """
    Wrapper around Location.objects.get_or_create just to use lru_cache
    """
    location, __ = Location.objects.get_or_create(
        street_address=street_address,
        city=city,
        state=state,
        zip=zip,
        defaults=dict(name=name),
    )
    return location


class Command(BaseCommand):
    help = "Import from Socrata API"

    def handle(self, *args, **options):
        res = requests.get(
            "https://data.texas.gov/resource/naix-2893.json",
            # What the params do:
            # https://dev.socrata.com/docs/queries/
            params={"$order": "obligation_end_date_yyyymmdd desc"},
        )
        data = res.json()
        print(len(data))
        for row in data:
            location = Location_get(
                street_address=row["taxpayer_address"],
                city=row["location_city"],
                state=row["location_state"],
                zip=row["location_zip"],
                name=row["location_name"],
            )
        #         receipt, created = obj_update_or_create(
        #             Receipt,
        #             tabc_permit=row["TABC Permit Number"],
        #             date=date_fmt(row["Obligation End Date"]),
        #             defaults=dict(
        #                 taxpayer_name=row["Taxpayer Name"],
        #                 tax_number=row["Taxpayer Number"],
        #                 liquor=row["Liquor Receipts"],
        #                 wine=row["Wine Receipts"],
        #                 beer=row["Beer Receipts"],
        #                 cover=row["Cover Charge Receipts"],
        #                 total=row["Total Receipts"],
        #                 location_name=row["Location Name"],
        #                 location_number=row["Location Number"],
        #                 county_code=row["Location County"],
        #                 location=location,
        #             ),
        #         )
