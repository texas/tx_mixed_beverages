from django.core.management.base import BaseCommand
from obj_update import obj_update_or_create
from tqdm import tqdm

from ...utils import assign_businesses, group_by_location


class Command(BaseCommand):
    help = "Do stuff after slurp"

    def handle(self, *args, **options):
        show_progress = True  # TODO add a way to silence progress bar
        print("assign_businesses")
        assign_businesses(show_progress=show_progress)
