import typing

from django.core.cache import cache
from django.core.management.base import BaseCommand
from django.db import connection

from indicators.models.data import CachedIndicatorData

if typing.TYPE_CHECKING:
    from psycopg2.extensions import cursor as _cursor


class Command(BaseCommand):
    help = "Delete all records stored in Indicator Data Store"

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            cursor: _cursor
            cursor.execute(f"TRUNCATE {CachedIndicatorData._meta.db_table}")
        cache.clear()
        print('✔️ Done')
