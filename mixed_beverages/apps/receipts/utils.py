import csv
import datetime
import os
from decimal import Decimal

from django.db.models import Count, Avg
from tqdm import tqdm

from .models import Receipt, Business, Location


def assign_businesses(show_progress=False):
    """
    Associates "Receipts" with businesses

    The initial run over 2.4MM receipts will take 4 hours
    """
    businesses_to_create = (
        Receipt.objects.filter(business=None)
        .values("tax_number", "taxpayer_name")
        .order_by("tax_number")
        .annotate(Count("tax_number"))
    )

    if not businesses_to_create:
        return

    for business_data in tqdm(businesses_to_create, disable=not show_progress):
        business, __ = Business.objects.get_or_create(
            tax_number=business_data["tax_number"],
            defaults=dict(name=business_data["taxpayer_name"]),
        )
        Receipt.objects.filter(
            tax_number=business_data["tax_number"], business=None
        ).update(business=business)


def set_location_data(show_progress=False):
    """
    Denormalizes receipt data into the `Location` model.

    timing: real    2m50.342s
    """
    latest_receipt_date = Receipt.objects.latest("date").date

    print(f"Set monthly receipts for the past 4 months, up to {latest_receipt_date}")
    queryset = Location.objects.all()
    # Good enough, go back 4 * 31 days to get 4 months
    cutoff_date = latest_receipt_date - datetime.timedelta(days=4 * 31)
    for x in tqdm(queryset, disable=not show_progress):
        receipt_stats = x.receipts.filter(total__gt=0, date__gt=cutoff_date).aggregate(
            Avg("total")
        )
        old_data = x.data or {}
        x.data = {
            **old_data,
            "avg_total": str(receipt_stats["total__avg"].quantize(Decimal(".01")))
            if receipt_stats["total__avg"]
            else "0",
        }
        x.save(update_fields=("data",))
