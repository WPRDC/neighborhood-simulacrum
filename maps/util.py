import json
import urllib.request
from typing import TYPE_CHECKING, Type
from urllib.error import URLError

from django.db import connection

from indicators.data import GeogCollection

if TYPE_CHECKING:
    from django.db.models.sql import Query
    from indicators.models import TimeAxis, Variable
    from geo.models import AdminRegion


def refresh_tile_index():
    """ Signal tile server to register new view """
    try:
        urllib.request.urlopen("http://127.0.0.1:3000/index.json")
    except URLError:
        pass


def as_tile_server_query(query: 'Query'):
    import re
    query_str = as_geometry_query(query)
    return re.sub(r',\s*\"geo_adminregion\".\"mini_geom\"\s*,', ',',
                  re.sub(r',\s*\"geo_adminregion\".\"geom\"\s*,', ',', query_str))


def as_geometry_query(query: 'Query'):
    """
    Removes casting of geometries to byte arrays as necessary for what django does
     but not useful as a raw postgis query
    :param query: QuerySet Query object to modify
    """
    return str(query).replace('::bytea', '')


def menu_view_name(geog_type: Type['AdminRegion']):
    return f'maps.v_{geog_type.geog_type_id.lower()}'


# noinspection SqlAmbiguousColumn ,SqlResolve
def store_map_data(
        map_slug: str,
        geog_collection: 'GeogCollection',
        time_axis: 'TimeAxis',
        variable: 'Variable',
        use_percent: bool
):
    table_name = f'maps.t_{map_slug}'
    view_name = f'maps.v_{map_slug}'

    data = variable.get_values(geog_collection, time_axis)
    number_format_options = {'style': 'percent'} if use_percent else variable.locale_options
    with connection.cursor() as cursor:
        cursor.execute(f"""DROP VIEW IF EXISTS {view_name}""")
        cursor.execute(f"""DROP TABLE IF EXISTS {table_name}""")
        cursor.execute(f"""CREATE TABLE {table_name} (geoid varchar(63), value numeric)""")
        sql_rows = [f"""('{datum.geog}', {datum.percent if use_percent else datum.value})""" for datum in data]
        cursor.execute(f"""INSERT INTO  {table_name} (geoid, value) VALUES """ + ", ".join(sql_rows))

        base_geography_subquery = as_geometry_query(geog_collection.geog_type.objects.filter(in_extent=True).query)

        cursor.execute(
            f"""CREATE VIEW {view_name} AS
                    SELECT 
                        geo.name as geo_name,
                        geo.geom as the_geom,
                        geo.geom_webmercator as the_geom_webmercator, 
                        %(title)s as title,
                        dat.value::float as value, 
                        %(number_format_options)s as number_format_options
                    FROM {table_name} dat
                    JOIN ({base_geography_subquery}) geo ON dat.geoid = geo.global_geoid""",
            {'title': variable.name, 'number_format_options': json.dumps(number_format_options)}
        )

        refresh_tile_index()


def store_menu_layer(geog_type: Type['AdminRegion']):
    print('Adding menu view for', geog_type.geog_type_id)
    view_name = menu_view_name(geog_type)
    view_query = as_tile_server_query(geog_type.objects.filter(in_extent=True).query)

    with connection.cursor() as cursor:
        cursor.execute(f"""DROP VIEW IF EXISTS {view_name}""")
        cursor.execute(f"""CREATE VIEW {view_name} AS {view_query}""")

    print('Menu view added.')

    refresh_tile_index()
