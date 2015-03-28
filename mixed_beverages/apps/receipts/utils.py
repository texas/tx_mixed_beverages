import csv
import os

from django.db.models import Count
from progressbar import ProgressBar

from .models import Receipt, Business, Location


def row_to_receipt(row):
    cleaned_row = map(str.strip, row)  # csv gives us `str` instead of unicode
    return Receipt(
        tabc_permit=cleaned_row[0],
        name=cleaned_row[1],
        address=cleaned_row[2],
        city=cleaned_row[3],
        state=cleaned_row[4],
        zip=cleaned_row[5],
        county_code=cleaned_row[6],
        # assign to the first of the month
        date='{}-{}-01'.format(*cleaned_row[8].split('/')),
        tax=cleaned_row[9],
    )


def slurp(path):
    """Import a csv."""
    assert os.path.isfile(path)
    with open(path, 'rb') as f:
        reader = csv.reader(f)
        receipts = []
        # TODO don't re-process csvs
        # TODO figure out business
        for row in reader:
            receipts.append(row_to_receipt(row))
        Receipt.objects.bulk_create(receipts)


def group_by_name(show_progress=False):
    names = (Receipt.objects.filter(business=None).values('name')
        .order_by('name').annotate(Count('name')))
    progress = ProgressBar()
    if not names:
        return
    for x in progress(names):
        name = x['name']
        business, __ = Business.objects.get_or_create(name=name)
        Receipt.objects.filter(business=None).update(business=business)


def group_by_location(show_progress=False):
    progress = ProgressBar() if show_progress else lambda x: x
    receipts_without_location = (Receipt.objects.filter(location=None)
        .order_by('address', 'city', 'state', 'zip'))
    if not receipts_without_location:
        return
    last_reference = None
    for x in progress(receipts_without_location):
        reference = dict(
            address=x.address,
            city=x.city,
            state=x.state,
            zip=x.zip,
        )
        if reference == last_reference:
            # the .update(...) and .order_by(...) makes this possible
            continue
        try:
            # look for an existing `Location`
            location = (Receipt.objects
                .filter(**reference).exclude(location=None)[0].location)
        except IndexError:
            # create a new `Location`
            location = Location.objects.create()
        receipts_without_location.filter(**reference).update(location=location)
        last_reference = reference


def post_process():
    group_by_name(show_progress=True)
    group_by_location(show_progress=True)


def geocode(wait=10):
    # TODO
    pass
