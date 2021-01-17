import os.path
from functools import lru_cache
from typing import List, Tuple

import requests

from django.core.management.base import BaseCommand
from obj_update import obj_update_or_create
from tqdm import tqdm

from ...models import Location, Receipt


@lru_cache(maxsize=512)
def Location_get(street_address, city, state, zip, name) -> Tuple[Location, bool]:
    """
    Wrapper around Location.objects.get_or_create just to use lru_cache
    """
    return Location.objects.get_or_create(
        street_address=street_address,
        city=city,
        state=state,
        zip=zip,
        defaults=dict(name=name),
    )


def import_data_from_api(data: List[dict]) -> int:
    created_count = 0
    for row in data:
        location, location_created = Location_get(
            street_address=row["taxpayer_address"],
            city=row["location_city"],
            state=row["location_state"],
            zip=row["location_zip"],
            name=row["location_name"],
        )
        if location_created:
            print(f"Created Location: {location}")
        receipt, created = obj_update_or_create(
            Receipt,
            tabc_permit=row["tabc_permit_number"],
            date=row["obligation_end_date_yyyymmdd"].split("T")[0],
            defaults=dict(
                taxpayer_name=row["taxpayer_name"],
                tax_number=row["taxpayer_number"],
                liquor=row["liquor_receipts"],
                wine=row["wine_receipts"],
                beer=row["beer_receipts"],
                cover=row["cover_charge_receipts"],
                total=row["total_receipts"],
                location_name=row["location_name"],
                location_number=row["location_number"],
                county_code=row["location_county"],
                location=location,
            ),
        )
        if created:
            created_count + 1
    return created_count


class Command(BaseCommand):
    help = "Import from Socrata API"

    def handle(self, *args, **options):
        offset = 0
        while True:
            res = requests.get(
                "https://data.texas.gov/resource/naix-2893.json",
                # What the params do:
                # https://dev.socrata.com/docs/queries/
                params={
                    "$order": "obligation_end_date_yyyymmdd desc",
                    "$offset": offset,
                    "$limit": 2000,  # Default: 1000
                },
            )
            data = res.json()
            print(f"Total rows: {len(data)}")
            print(
                f'Date range: {data[0]["obligation_end_date_yyyymmdd"]} - {data[-1]["obligation_end_date_yyyymmdd"]}'
            )
            created_acount = import_data_from_api(data)
            print(f"Created   : {created_count}")
            if created_count:
                offset += len(data)
            else:
                break
