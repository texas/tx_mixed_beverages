import json

from django.core.management.base import BaseCommand

from mixed_beverages.apps.receipts.models import Location


class Command(BaseCommand):
    help = "Create a backup of address -> geolocation data to stdout"

    def handle(self, *args, **options):
        for location in Location.objects.exclude(coordinate=None):
            self.stdout.write(
                json.dumps(
                    {
                        "streetAddress": location.address,
                        "city": location.city,
                        "state": location.state,
                        "zip": location.zip,
                        "coordinate": str(location.coordinate),
                        "coordinate_quality": str(location.coordinate_quality),
                    }
                )
            )
