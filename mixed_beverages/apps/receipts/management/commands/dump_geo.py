from __future__ import unicode_literals

import json

from django.core.management.base import BaseCommand

from mixed_beverages.apps.receipts.models import Location


class Command(BaseCommand):
    help = 'Create a backup of geo data to stdout'

    def handle(self, *args, **options):
        """
        I hate csv right now.
        """
        for location in Location.objects.exclude(coordinate=None):
            latest = location.get_latest()
            self.stdout.write(json.dumps({
                'streetAddress': latest.address,
                'city': latest.city,
                'state': latest.state,
                'zip': latest.zip,
                'coordinate': unicode(location.coordinate),
                'coordinate_quality': location.coordinate_quality,
            }))
