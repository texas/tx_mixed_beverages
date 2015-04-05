from __future__ import unicode_literals

import json
import os

from django.core.management.base import BaseCommand, CommandError

from mixed_beverages.apps.receipts.models import Receipt, Location


class Command(BaseCommand):
    help = 'Load a backup of geo data'

    def add_arguments(self, parser):
        parser.add_argument('infile', nargs=1)

    def handle(self, **options):
        """
        Assumes post_process step already ran to bundle receipts by location.
        """
        infile = options['infile'][0]
        if not os.path.isfile(infile):
            raise CommandError('{} is not a file'.format(infile))

        with open(infile, 'rb') as fh:
            for line in fh:
                data = json.loads(line)
                try:
                    receipt = Receipt.objects.filter(
                        address=data['streetAddress'],
                        city=data['city'],
                        state=data['state'],
                        zip=data['zip'],
                    )[0]
                except IndexError:
                    print('No match')
                    continue
                try:
                    location = receipt.location
                except Location.DoesNotExist:
                    raise CommandError('run `make process` first')
                if location.coordinate:
                    # don't overwrite existing coordinate data
                    continue
                location.coordinate = data['coordinate']
                location.coordinate_quality = data['coordinate_quality']
