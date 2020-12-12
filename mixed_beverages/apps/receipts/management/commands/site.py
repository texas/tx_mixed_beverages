import os.path

from django.core.management.base import BaseCommand
from django.db.models import Q
from tqdm import tqdm

from mixed_beverages.apps.lazy_geo.views import location_detail
from mixed_beverages.apps.receipts.models import Location


class Command(BaseCommand):
    help = """
    Dump json responses for locations. Not using wget to speed things up
    """

    def add_arguments(self, parser):
        parser.add_argument(
            "--overwrite",
            action="store_true",
            help="Overwrite existing location data, will slow deploy",
        )

    def handle(self, overwrite, *args, **options):
        qs = (
            Location.objects.filter(coordinate__isnull=False)
            .exclude(Q(data__avg_total="0") | Q(data__avg_total="0.00"))
            .prefetch_related("receipts")
        )
        self.stdout.write("Generating location detail json files")
        for location in tqdm(qs):
            res = location_detail(None, location.pk)

            path = f"_site/location/{location.pk}.json"
            if os.path.isfile(path) and not overwrite:
                continue

            with open(path, "wb") as fh:
                fh.write(res.content)
