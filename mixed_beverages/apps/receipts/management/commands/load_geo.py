import json
import os

from django.core.management.base import BaseCommand, CommandError
from tqdm import tqdm

from mixed_beverages.apps.receipts.models import Location


class Command(BaseCommand):
    help = "Load a backup of geo data"

    def add_arguments(self, parser):
        parser.add_argument("infile", nargs=1)

    def handle(self, **options):
        """
        Assumes post_process step already ran to bundle receipts by location.
        """
        infile = options["infile"][0]
        if not os.path.isfile(infile):
            raise CommandError(f"{infile} is not a file")

        with open(infile) as fh:
            total_lines = sum(1 for _ in fh)
            fh.seek(0)

            for line in tqdm(fh, total=total_lines, desc="Loading geo data"):
                data = json.loads(line)
                street_address = data["streetAddress"].split("\n")[0]
                try:
                    location = Location.objects.get(
                        street_address=street_address,
                        city=data["city"],
                        state=data["state"],
                        zip=data["zip"],
                    )
                except Location.DoesNotExist:
                    self.stderr.write(f"No match for {street_address}")
                    continue
                if location.coordinate:
                    # don't overwrite existing coordinate data
                    continue
                location.coordinate = data["coordinate"]
                location.coordinate_quality = data["coordinate_quality"]
                location.save()
