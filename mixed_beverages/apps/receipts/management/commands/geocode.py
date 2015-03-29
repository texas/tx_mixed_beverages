from __future__ import unicode_literals

from time import sleep
import logging

from django.core.management.base import BaseCommand

from mixed_beverages.apps.receipts.models import Location
from mixed_beverages.apps.lazy_geo.utils import get_remaining_credits


class Command(BaseCommand):
    help = 'Geocode some addresses, waits 10 seconds'

    def add_arguments(self, parser):
        parser.add_argument('--random', dest='random', action='store_true',
            help='Pick addresses at random')
        parser.add_argument('--city', dest='city',
            help='Limit to a city')
        parser.add_argument('--wait', dest='wait', type=int, default=10,
            help='How many seconds to wait between requests')

    def handle(self, *args, **options):
        credit = get_remaining_credits()
        self.stdout.write('# of api credits remaining: {}'.format(credit))

        filter_kwargs = {'coordinate__isnull': True}
        if options['city']:
            filter_kwargs['receipts__city__iexact'] = options['city']
        # pull in the same order so it's repeatable
        queryset = (
            Location.objects.filter(**filter_kwargs).distinct()
        )
        self.stdout.write('# of addresses to geocode: {}'.format(queryset.count()))
        verbosity = int(options['verbosity'])
        if verbosity == 1:
            logging.getLogger('geocode').setLevel(logging.INFO)
        elif verbosity > 1:
            self.stdout.write(unicode(filter_kwargs))
            logging.getLogger('geocode').setLevel(logging.DEBUG)
        if verbosity > 2:
            logging.getLogger().setLevel(logging.DEBUG)

        if options['random']:
            # not very efficient, but is terse
            queryset = queryset.order_by('?')

        try:
            for location in queryset[:credit]:
                location.geocode()
                sleep(options['wait'])
        except KeyboardInterrupt:
            exit('bye')
