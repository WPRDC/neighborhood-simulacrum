from django.core.management.base import BaseCommand
from . import _load_census as census_loader


class Command(BaseCommand):
    help = "Load standard geographies"

    def add_arguments(self, parser):
        parser.add_argument('-s', '--start', type=int, default=1)
        parser.add_argument('-e', '--end', type=int, default=141)
        parser.add_argument('-y', '--year', type=int, default=2019)
        parser.add_argument('-D', '--delete', action='store_true')

    def handle(self, *args, **options):
        year = options.get('year', 2019)
        census_loader.run(options['start'], options['end'], year=year, delete=options['delete'])
