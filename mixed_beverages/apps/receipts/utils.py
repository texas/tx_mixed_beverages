from __future__ import unicode_literals

import csv
import datetime
import os

from django.db.models import Count
from progressbar import ProgressBar

from .models import Receipt, Business, Location


# Receipt.objects.latest('date').date
latest_receipt_date = datetime.date(2015, 3, 1)  # TODO set this at import time


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


def slurp(path, force=False):
    """Import a csv."""
    assert os.path.isfile(path)
    source = os.path.basename(path)
    if Receipt.objects.filter(source=source).exists():
        print('already imported {}'.format(source))
        return
    with open(path, 'rb') as f:
        reader = csv.reader(f)
        receipts = []
        for row in reader:
            receipt = row_to_receipt(row)
            receipt.source = source
            receipts.append(receipt)
        Receipt.objects.bulk_create(receipts)


def group_by_name(show_progress=False):
    progress = ProgressBar() if show_progress else lambda x: x
    names = (Receipt.objects.filter(business=None).values('name')
        .order_by('name').annotate(Count('name')))
    progress = ProgressBar()
    if not names:
        return
    for x in progress(names):
        name = x['name']
        business, __ = Business.objects.get_or_create(name=name)
        (Receipt.objects
            .filter(name=name, business=None).update(business=business))


def group_by_location(show_progress=False):
    """
    Group businesses by location.

    Optimized for making the initial import faster.
    """
    progress = ProgressBar() if show_progress else lambda x: x
    receipts_without_location = (Receipt.objects.filter(location=None)
        .order_by('address', 'city', 'state', 'zip'))
    if not receipts_without_location:
        return
    last_reference = None
    for x in progress(receipts_without_location):
        # TODO is grouping by `tabc_permit` the same thing?
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


def set_location_data(show_progress=False):
    progress = ProgressBar() if show_progress else lambda x: x
    queryset = Location.objects.all()
    # good enough, go back 4 * 31 days to get 4 months
    cutoff_date = latest_receipt_date - datetime.timedelta(days=124)
    for x in progress(queryset):
        latest_receipts = list(x.receipts.filter(date__gt=cutoff_date)
                               .order_by('-date')[:4])
        if not latest_receipts:
            if x.data:
                # clear old data
                x.data = {}
                x.save(update_fields=('data', ))
            continue
        latest_receipt = latest_receipts[0]
        avg_tax = sum(x.tax for x in latest_receipts) / len(latest_receipts)
        # remember that hstore only stores text
        x.data = {
            'name': unicode(latest_receipt.name),
            'avg_tax': '{:.2f}'.format(avg_tax),
        }
        x.save(update_fields=('data', ))


def post_process():
    show_progress = True  # TODO add a way to silence progress bar
    print 'group_by_name'
    group_by_name(show_progress=show_progress)
    print 'group_by_location'
    group_by_location(show_progress=show_progress)
    print 'set_location_data'
    set_location_data(show_progress=show_progress)
