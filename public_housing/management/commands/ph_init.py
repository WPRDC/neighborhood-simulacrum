from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import connection

from maps.util import refresh_tile_index, as_tile_server_query
from public_housing.models import ProjectIndex


class Command(BaseCommand):
    help = "Handles scripting that needs to be done to initialize public housing data."

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        # create map view for use in tile server
        print('Adding map view of all public housing projects.')
        view_name = f'maps.v_{settings.PUBLIC_HOUSING_PROJECT_LAYER_VIEW}'
        source_table = ProjectIndex._meta.db_table

        view_query = as_tile_server_query(f"""
            SELECT *
            FROM (
                SELECT 
                id, property_id, hud_property_name, property_street_address, municipality_name, city,
                zip_code, units, scattered_sites, latitude, longitude, census_tract, crowdsourced_id, house_cat_id, status,
                ST_Transform(ST_SetSRID(ST_Point(longitude::numeric, latitude::numeric), 4326), 3857)::geometry(point,3857) as geom_webmercator
                --- ST_SetSRID(ST_Point(longitude::numeric, latitude::numeric), 4326)::geometry(point,4326) as geom
                
                FROM "datastore"."{source_table}" 
            WHERE latitude IS NOT NULL AND longitude IS NOT NULL
            ) source_table
        """.lstrip())



        print(view_query)

        with connection.cursor() as cursor:
            cursor.execute(f"""DROP MATERIALIZED VIEW IF EXISTS {view_name}""")
            cursor.execute(f"""CREATE MATERIALIZED VIEW {view_name} AS {view_query}""")

        print('Projects map view added!')
        refresh_tile_index()
