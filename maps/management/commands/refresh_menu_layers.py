import typing

import psycopg2.extras
from django.core.management.base import BaseCommand

from geo.models import AdminRegion
from maps.models import DataLayer
from django.db import connection

from maps.util import store_menu_layer

if typing.TYPE_CHECKING:
    from psycopg2.extensions import cursor as _cursor


class Command(BaseCommand):
    help = "Delete DataLayers and clear all map views from database."

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        print('🏗 Rebuilding menu layers')
        for geog_type in AdminRegion.__subclasses__():
            store_menu_layer(geog_type)
        print('✔️ Done')
