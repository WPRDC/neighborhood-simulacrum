import typing

import psycopg2.extras
from django.core.management.base import BaseCommand

from maps.models import IndicatorLayer
from django.db import connection

if typing.TYPE_CHECKING:
    from psycopg2.extensions import cursor as _cursor


class Command(BaseCommand):
    help = "Delete DataLayers and clear all map views from database."

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        print('Deleting all DataLayers')
        num, counts = IndicatorLayer.objects.all().delete()
        if num:
            print(counts['maps.DataLayer'], 'DataLayers deleted.')


        print('Dropping orphaned map views and tables')
        with connection.cursor() as cursor:
            cursor: _cursor
            cursor.execute("""
                DROP SCHEMA IF EXISTS maps CASCADE;
                CREATE SCHEMA maps AUTHORIZATION profiles_user;
                GRANT USAGE ON SCHEMA maps TO profiles_maps_user;
                GRANT SELECT ON ALL TABLES IN SCHEMA maps TO profiles_maps_user;
                -- when profiles generates new map tables and views, give SELECT to the maps user by default
                ALTER DEFAULT PRIVILEGES 
                    FOR USER profiles_user 
                    IN SCHEMA maps 
                    GRANT SELECT ON TABLES TO profiles_maps_user;
            """)
        print('✔️ Done')
