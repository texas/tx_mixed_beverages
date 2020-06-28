from django.core.management.base import BaseCommand
from ... import models


class Command(BaseCommand):
    help = "Import a CSV file"

    def add_arguments(self, parser):
        parser.add_argument("csv")

    def handle(self, csv, *args, **options):
        print(csv)
