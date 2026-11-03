import time

from django.contrib.gis.geos import Point
from django.core.management.base import BaseCommand

from mixed_beverages.apps.receipts import geocodio
from mixed_beverages.apps.receipts.models import Location


class Command(BaseCommand):
    help = """
    Geocode locations missing coordinates with the Geocodio API, highest recent
    business (Location.data["avg_total"]) first.
    """

    def add_arguments(self, parser):
        parser.add_argument(
            "--limit",
            type=int,
            default=None,
            help="Only geocode up to this many locations",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be geocoded; make no API calls",
        )

    def handle(self, limit, dry_run, *args, **options):
        qs = geocodio.order_by_recent_business(
            Location.objects.filter(coordinate__isnull=True)
        ).filter(avg_total__gt=0)  # skip idle (0) and unknown (null) locations
        total = qs.count()
        if limit is not None:
            qs = qs[:limit]
        selected = list(qs)

        self.stdout.write(f"Locations missing coordinates: {total}")
        self.stdout.write(f"Locations selected: {len(selected)}")
        if not selected:
            return
        first, last = selected[0], selected[-1]
        self.stdout.write(f"First: pk={first.pk} avg_total={first.avg_total}")
        self.stdout.write(f"Last: pk={last.pk} avg_total={last.avg_total}")
        if dry_run:
            return

        start = time.perf_counter()
        results = geocodio.geocode(geocodio.get_api_key(), selected)
        updated = []
        for location, result in zip(selected, results, strict=True):
            if result is None:
                continue
            lat, lng, accuracy = result
            location.coordinate = Point(x=lng, y=lat)
            location.coordinate_quality = accuracy
            updated.append(location)
        Location.objects.bulk_update(updated, ["coordinate", "coordinate_quality"])
        elapsed = time.perf_counter() - start
        self.stdout.write(
            f"Matched {len(updated)} of {len(selected)} in {elapsed:.1f}s "
            f"({elapsed / len(selected):.3f}s per location)"
        )
