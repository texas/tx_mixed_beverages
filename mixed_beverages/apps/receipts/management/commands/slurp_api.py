from decimal import Decimal
from functools import lru_cache

import requests
from django.core.management.base import BaseCommand
from obj_update import obj_update

from ...models import Location, Receipt


@lru_cache(maxsize=512)
def location_get(street_address, city, state, zip_code, name) -> tuple[Location, bool]:
    """
    Wrapper around Location.objects.get_or_create just to use lru_cache
    """
    return Location.objects.get_or_create(
        street_address=street_address,
        city=city,
        state=state,
        zip=zip_code,
        defaults={"name": name},
    )


def import_data_from_api(data: list[dict]) -> tuple[int, int]:
    created_count = 0
    updated_count = 0
    for row in data:
        location, location_created = location_get(
            street_address=row["location_address"],
            city=row["location_city"],
            state=row["location_state"],
            zip_code=row["location_zip"],
            name=row["location_name"],
        )
        if location_created:
            print(f"Created Location: {location.pk} - {location}")
        money = Decimal("0.01")
        defaults = {
            "taxpayer_name": row["taxpayer_name"],
            "tax_number": row["taxpayer_number"],
            "liquor": Decimal(row["liquor_receipts"]).quantize(money),
            "wine": Decimal(row["wine_receipts"]).quantize(money),
            "beer": Decimal(row["beer_receipts"]).quantize(money),
            "cover": Decimal(row["cover_charge_receipts"]).quantize(money),
            "total": Decimal(row["total_receipts"]).quantize(money),
            "location_name": row["location_name"],
            "location_number": row["location_number"],
            "county_code": row["location_county"],
            "location": location,
        }
        receipt, created = Receipt.objects.get_or_create(
            tabc_permit=row["tabc_permit_number"],
            date=row["obligation_end_date_yyyymmdd"].split("T")[0],
            defaults=defaults,
        )
        if created:
            created_count += 1
        elif obj_update(receipt, defaults):
            updated_count += 1
    return created_count, updated_count


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
            if not data:
                break
            print(f"Total rows: {len(data)}")
            print(
                f"Date range: {data[0]['obligation_end_date_yyyymmdd']} - "
                f"{data[-1]['obligation_end_date_yyyymmdd']}"
            )
            created_count, updated_count = import_data_from_api(data)
            print(f"Created : {created_count}")
            print(f"Updated : {updated_count}")
            if created_count or updated_count:
                offset += len(data)
            else:
                break
