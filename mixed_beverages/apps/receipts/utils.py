import csv
import os
import sys

from .models import Receipt


def process_row(row):
    return Receipt(
        permit=row[0],
        name=row[1],
        date='{}-{}-01'.format(*row[8].split('/')),
        tax=row[9],
        address=row[2],
        city=row[3],
        state=row[4],
        zip=row[5],
        county_code=row[6],
    )


def slurp(path):
    assert os.path.isfile(path)
    with open(path, 'rb') as f:
        reader = csv.reader(f)
        receipts = []
        # TODO don't re-process csvs
        # TODO figure out business
        for row in reader:
            receipts.append(process_row(row))
        Receipt.objects.bulk_create(receipts)


if __name__ == '__main__':
    import django; django.setup()  # noqa
    slurp(*sys.argv[1:])
