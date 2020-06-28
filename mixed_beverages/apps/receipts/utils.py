import csv
import datetime
import os

from django.db.models import Count
from tqdm import tqdm

from .models import Receipt, Business, Location


def row_to_receipt(row):
    cleaned_row = list(map(str.strip, row))
    if len(cleaned_row[0]) > 8:
        return None

    return Receipt(
        tabc_permit=cleaned_row[0],
        name=cleaned_row[1],
        address=cleaned_row[2],
        city=cleaned_row[3],
        state=cleaned_row[4],
        zip=cleaned_row[5],
        county_code=cleaned_row[6],
        # assign to the first of the month
        date="{}-{}-01".format(*cleaned_row[8].split("/")),
        tax=cleaned_row[9],
    )


def slurp(path, force=False):
    """Import a csv."""
    assert os.path.isfile(path)
    source = os.path.basename(path)
    if Receipt.objects.filter(source=source).exists():
        print("already imported {}".format(source))
        return

    with open(path, "r", encoding="windows-1252") as f:
        reader = csv.reader(f)
        receipts = []
        for row in reader:
            receipt = row_to_receipt(row)
            if receipt is None:
                continue

            receipt.source = source
            receipts.append(receipt)
        Receipt.objects.bulk_create(receipts)


def group_by_name(show_progress=False):
    names = (
        Receipt.objects.filter(business=None)
        .values("name")
        .order_by("name")
        .annotate(Count("name"))
    )
    if not names:
        return

    for x in tqdm(names, disable=not show_progress):
        name = x["name"]
        business, __ = Business.objects.get_or_create(name=name)
        (Receipt.objects.filter(name=name, business=None).update(business=business))


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
        avg_tax = sum(x.tax for x in recent_receipts) / len(recent_receipts)
        # remember that hstore only stores text
        x.data = {
            "name": str(latest_receipt.name),
            "avg_tax": "{:.2f}".format(avg_tax),
        }
        x.save(update_fields=("data",))


def post_process():
    show_progress = True  # TODO add a way to silence progress bar
    print("group_by_name")
    group_by_name(show_progress=show_progress)
    print("group_by_location")
    group_by_location(show_progress=show_progress)
    print("set_location_data")
    set_location_data(show_progress=show_progress)
