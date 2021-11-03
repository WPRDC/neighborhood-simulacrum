import typing

from django.core.management.base import BaseCommand

from geo.models import AdminRegion
from maps.util import store_menu_layer

if typing.TYPE_CHECKING:
    pass


class Command(BaseCommand):
    help = "Add or update basic geography tile layers for use in menus."

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        print('🏗 Rebuilding menu layers')
        for geog_type in AdminRegion.__subclasses__():
            store_menu_layer(geog_type)
        print('✔️ Done')
