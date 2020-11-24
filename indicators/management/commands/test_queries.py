from django.core.management.base import BaseCommand

from indicators.management.commands import _test_queries


class Command(BaseCommand):
    help = "Load generated indicators"

    def add_arguments(self, parser):
        # todo: add arguments that map to the `load_census_boundaries.run()` ones
        pass

    def handle(self, *args, **options):
        _test_queries.run()