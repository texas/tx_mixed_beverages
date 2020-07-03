from django.core.management.base import BaseCommand
from obj_update import obj_update_or_create
from tqdm import tqdm

from ...utils import assign_businesses, set_location_data


class Command(BaseCommand):
    help = "Do stuff after slurp"

    def handle(self, *args, **options):
        show_progress = True  # TODO add a way to silence progress bar
        print("assign_businesses")
        assign_businesses(show_progress=show_progress)
        set_location_data(show_progress=show_progress)
