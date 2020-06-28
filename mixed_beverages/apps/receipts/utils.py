import csv
import datetime
import os

from django.db.models import Count
from tqdm import tqdm

from .models import Receipt, Business, Location


def assign_businesses(show_progress=False):
    tax_numbers_to_assign = Receipt.objects.filter(business=None).values("tax_number")
    if not tax_numbers_to_assign:
        return

    for tax_number in tqdm(tax_numbers_to_assign, disable=not show_progress):
        business, __ = Business.objects.get_or_create(tax_number=tax_number)
        # FIXME business needs a name!
        Receipt.objects.filter(tax_number=tax_number, business=None).update(
            business=business
        )


def group_by_location(show_progress=False):
    """
    Group businesses by location.

    Optimized for making the initial import faster.
    FIXME this is really slow
    """
    receipts_without_location = Receipt.objects.filter(location=None).order_by(
        "address", "city", "state", "zip"
    )
    if not receipts_without_location:
        return

    last_reference = None
    for x in tqdm(receipts_without_location, disable=not show_progress):
        # TODO is grouping by `tabc_permit` the same thing?
        reference = dict(address=x.address, city=x.city, state=x.state, zip=x.zip,)
        if reference == last_reference:
            # the .update(...) and .order_by(...) makes this possible
            continue

        try:
            # look for an existing `Location`
            location = (
                Receipt.objects.filter(**reference).exclude(location=None)[0].location
            )
        except IndexError:
            # create a new `Location`
            location = Location.objects.create()
        receipts_without_location.filter(**reference).update(location=location)
        last_reference = reference


def set_location_data(show_progress=False):
    """
    Denormalizes data into the `Location` model.

    timing: real    2m50.342s
    """
    latest_receipt_date = Receipt.objects.latest("date").date

    queryset = Location.objects.all()
    # good enough, go back 4 * 31 days to get 4 months
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
        # remember that hstore only stores text
        x.data = {
            "name": str(latest_receipt.name),
            "avg_tax": "{:.2f}".format(avg_tax),
        }
        x.save(update_fields=("data",))
