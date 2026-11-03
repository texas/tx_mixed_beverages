import time
from decimal import Decimal

from django.contrib.gis.geos import Point
from django.core.management.base import BaseCommand

from mixed_beverages.apps.receipts import geocodio
from mixed_beverages.apps.receipts.models import Location


class Command(BaseCommand):
    help = """
    Re-geocode locations that already have a low quality coordinate, highest
    recent business (Location.data["avg_total"]) first. A new result is saved
    only if its accuracy beats the stored one. Locations without coordinates
    are the `geocode` command's job.
    """

    def add_arguments(self, parser):
        parser.add_argument(
            "--limit",
            type=int,
            default=100,
            help="Only re-geocode up to this many locations (default: 100)",
        )
        parser.add_argument(
            "--max-quality",
            type=Decimal,
            default=Decimal("0.6"),
            help="Re-geocode locations with a quality below this (default: 0.6)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be re-geocoded; make no API calls",
        )

    def handle(self, limit, max_quality, dry_run, *args, **options):
        qs = geocodio.order_by_recent_business(
            Location.objects.filter(
                coordinate__isnull=False, coordinate_quality__lt=max_quality
            )
        )
        total = qs.count()
        if limit is not None:
            qs = qs[:limit]
        selected = list(qs)

        self.stdout.write(f"Locations with quality below {max_quality}: {total}")
        self.stdout.write(f"Locations selected: {len(selected)}")
        if not selected:
            return
        first, last = selected[0], selected[-1]
        self.stdout.write(
            f"First: pk={first.pk} avg_total={first.avg_total} "
            f"quality={first.coordinate_quality}"
        )
        self.stdout.write(
            f"Last: pk={last.pk} avg_total={last.avg_total} "
            f"quality={last.coordinate_quality}"
        )
        if dry_run:
            return

        start = time.perf_counter()
        results = geocodio.geocode(geocodio.get_api_key(), selected)
        updated = []
        for location, result in zip(selected, results, strict=True):
            if result is None:
                continue
            lat, lng, accuracy = result
            if accuracy <= location.coordinate_quality:
                continue
            location.coordinate = Point(x=lng, y=lat)
            location.coordinate_quality = accuracy
            updated.append(location)
        Location.objects.bulk_update(updated, ["coordinate", "coordinate_quality"])
        elapsed = time.perf_counter() - start
        still_low = sum(x.coordinate_quality < max_quality for x in selected)
        self.stdout.write(
            f"Improved {len(updated)} of {len(selected)} in {elapsed:.1f}s; "
            f"{still_low} still below {max_quality}"
        )
