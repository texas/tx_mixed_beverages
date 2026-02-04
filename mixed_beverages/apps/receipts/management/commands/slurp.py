import csv as csv_lib
import os.path
import subprocess
from functools import lru_cache

from django.core.management.base import BaseCommand
from tqdm import tqdm

from ...models import Location, Receipt


def date_fmt(date: str):
    """Convert m/d/y to Y-M-D"""
    try:
        month, day, year = date.split("/")
        return f"{year}-{month}-{day}"

    except Exception:
        return None


@lru_cache(maxsize=10000)
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
    help = "Import a CSV file. Bulk insert with upsert for fast import."

    """
    Deduplication Strategy:
    - The source data contains duplicate entries where the same TABC permit + date
      appears multiple times with different location names (e.g., venue name vs. event name)
    - We keep the entry with the LOWEST location_number, which typically represents
      the permanent venue rather than the temporary event name
    - Example: TB015938 on 2007-10-31
      - Location #1: "Randy's Cafe" (venue) - KEPT
      - Location #3: "Courtney Wedding Reception" (event) - DROPPED
    """

    def add_arguments(self, parser):
        parser.add_argument("csv")

    def handle(self, csv, *args, **options):
        assert os.path.isfile(csv)

        # Fast row count using wc -l (subtract 1 for header)
        row_count = (
            int(subprocess.check_output(["wc", "-l", csv]).decode().split()[0]) - 1
        )

        BATCH_SIZE = 5000
        receipts_batch = []

        with open(csv, encoding="windows-1252") as fh:
            reader = csv_lib.DictReader(fh)

            for row in tqdm(reader, total=row_count):
                location = location_get(
                    street_address=row["Location Address"],
                    city=row["Location City"],
                    state=row["Location State"],
                    zip_code=row["Location Zip"],
                    name=row["Location Name"],
                )

                receipts_batch.append(
                    Receipt(
                        tabc_permit=row["TABC Permit Number"],
                        date=date_fmt(row["Obligation End Date"]),
                        taxpayer_name=row["Taxpayer Name"],
                        tax_number=row["Taxpayer Number"],
                        liquor=row["Liquor Receipts"],
                        wine=row["Wine Receipts"],
                        beer=row["Beer Receipts"],
                        cover=row["Cover Charge Receipts"],
                        total=row["Total Receipts"],
                        location_name=row["Location Name"],
                        location_number=row["Location Number"],
                        county_code=row["Location County"],
                        location=location,
                    )
                )

                if len(receipts_batch) >= BATCH_SIZE:
                    # Deduplicate: keep venue (lowest location_number) for each (permit, date)
                    seen = {}
                    for receipt in receipts_batch:
                        key = (receipt.tabc_permit, receipt.date)
                        if key not in seen:
                            seen[key] = receipt
                        else:
                            # Keep the one with lower location_number (the venue)
                            if receipt.location_number < seen[key].location_number:
                                seen[key] = receipt

                    deduped_batch = list(seen.values())

                    Receipt.objects.bulk_create(
                        deduped_batch,
                        update_conflicts=True,
                        unique_fields=["tabc_permit", "date"],
                        update_fields=[
                            "taxpayer_name",
                            "tax_number",
                            "liquor",
                            "wine",
                            "beer",
                            "cover",
                            "total",
                            "location_name",
                            "location_number",
                            "county_code",
                            "location",
                        ],
                    )
                    receipts_batch = []

            # Insert final batch
            if receipts_batch:
                # Deduplicate: keep venue (lowest location_number) for each (permit, date)
                seen = {}
                for receipt in receipts_batch:
                    key = (receipt.tabc_permit, receipt.date)
                    if key not in seen:
                        seen[key] = receipt
                    else:
                        # Keep the one with lower location_number (the venue)
                        if receipt.location_number < seen[key].location_number:
                            seen[key] = receipt

                deduped_batch = list(seen.values())

                Receipt.objects.bulk_create(
                    deduped_batch,
                    update_conflicts=True,
                    unique_fields=["tabc_permit", "date"],
                    update_fields=[
                        "taxpayer_name",
                        "tax_number",
                        "liquor",
                        "wine",
                        "beer",
                        "cover",
                        "total",
                        "location_name",
                        "location_number",
                        "county_code",
                        "location",
                    ],
                )
