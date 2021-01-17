from django.test import TestCase

from .slurp_api import import_data_from_api


class SlurpApiTests(TestCase):
    def test_trivial_nothing_happens_with_no_data(self):
        created_count = import_data_from_api([])
        self.assertEqual(created_count, 0)
