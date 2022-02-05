import argparse

from django.core.management import BaseCommand
from django.db.transaction import atomic

from geo.models import AdminRegion


class Command(BaseCommand):
    help = "Load standard geographies"

    def add_arguments(self, parser: argparse.ArgumentParser):
        pass

    def handle(self, *args, **options):
        regions = AdminRegion.objects.filter(in_extent=True)

        @atomic
        def lot_of_saves(queryset):
            for item in queryset:
                print(item)
                item.save()

        lot_of_saves(regions)
