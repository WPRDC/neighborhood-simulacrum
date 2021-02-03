from django.core.management.base import BaseCommand
from . import _load_census as census_loader


class Command(BaseCommand):
    help = "Load standard geographies"

    def add_arguments(self, parser):
        parser.add_argument('start', nargs=1, type=int)
        parser.add_argument('end', nargs=1, type=int)
        pass

    def handle(self, *args, **options):
        print(options)
        census_loader.run(options['start'][0], options['end'][0])
