import csv
import os

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


def post_process():
    for receipt in Receipt.objects.filter():
        pass
