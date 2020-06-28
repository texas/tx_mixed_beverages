import os.path
import csv as csv_lib

from django.core.management.base import BaseCommand
from ... import models


class Command(BaseCommand):
    help = "Import a CSV file"

    def add_arguments(self, parser):
        parser.add_argument("csv")

    def handle(self, csv, *args, **options):
        assert os.path.isfile(csv)

        with open(csv, "r", encoding="windows-1252") as fh:
            reader = csv_lib.DictReader(fh)
            for row in reader:
                print(row)
                break
            #     receipt = row_to_receipt(row)
            #     if receipt is None:
            #         continue

            #     receipt.source = source
            #     receipts.append(receipt)
            # Receipt.objects.bulk_create(receipts)
