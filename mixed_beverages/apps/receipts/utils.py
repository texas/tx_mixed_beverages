import csv
import datetime
import os

from django.db.models import Count
from tqdm import tqdm

from .models import Receipt, Business, Location


def assign_businesses(show_progress=False):
    businesses_to_create = (
        Receipt.objects.filter(business=None)
        .values("tax_number", "name")
        .order_by("tax_number")
        .annotate(Count("tax_number"))
    )

    if not businesses_to_create:
        return

    for business_data in tqdm(businesses_to_create, disable=not show_progress):
        business, __ = Business.objects.get_or_create(
            tax_number=business_data["tax_number"],
            defaults=dict(name=business_data["name"]),
        )
        Receipt.objects.filter(
            tax_number=business_data["tax_number"], business=None
        ).update(business=business)


def set_location_data(show_progress=False):
    """
    Denormalizes data into the `Location` model.

    timing: real    2m50.342s
    """
    latest_receipt_date = Receipt.objects.latest("date").date

    queryset = Location.objects.all()
    # Good enough, go back 4 * 31 days to get 4 months
    cutoff_date = latest_receipt_date - datetime.timedelta(days=4 * 31)
    for x in tqdm(queryset, disable=not show_progress):
        latest_receipts = list(x.receipts.order_by("-date")[:4])
        latest_receipt = latest_receipts[0]
        recent_receipts = list(filter(lambda x: x.date > cutoff_date, latest_receipts))
        if not recent_receipts:
            # clear old data
            x.data = {
                "name": str(latest_receipt.name),
                "avg_tax": "0",
            }
            x.save(update_fields=("data",))
            continue
        avg_tax = sum(x.total for x in recent_receipts) / len(recent_receipts)
        x.data = {
            "name": str(latest_receipt.name),
            "avg_tax": "{:.2f}".format(avg_tax),
        }
        x.save(update_fields=("data",))
