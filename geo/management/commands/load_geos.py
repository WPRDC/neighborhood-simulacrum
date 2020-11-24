from django.core.management.base import BaseCommand
from ...bin import load_census_boundaries

class Command(BaseCommand):
    help = "Load standard geographies"

    def add_arguments(self, parser):
        # todo: add arguments that map to the `load_census_boundaries.run()` ones
        pass

    def handle(self, *args, **options):
        load_census_boundaries.run()
