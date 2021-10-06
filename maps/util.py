import json
import urllib.request
from typing import TYPE_CHECKING, Type

from django.db import connection
from django.db.models import QuerySet

from indicators.utils import limit_to_geo_extent

if TYPE_CHECKING:
    from django.db.models.sql import Query
    from indicators.models import TimeAxis, Variable
    from geo.models import AdminRegion


def as_geometry_query(query: 'Query'):
    """
    Removes casting of geometries to byte arrays as necessary for what django does
     but not useful as a raw postgis query
    :param query: QuerySet Query object to modify
    """
    return str(query).replace('::bytea', '')


# noinspection SqlAmbiguousColumn ,SqlResolve
def store_map_data(map_slug: str,
                   geog_type: Type['AdminRegion'],
                   time_axis: 'TimeAxis',
                   variable: 'Variable',
                   use_percent: bool):
    table_name = f'maps.t_{map_slug}'
    view_name = f'maps.v_{map_slug}'

    # todo: handle this properly, likely using generic types
    # noinspection PyTypeChecker
    geogs: QuerySet['AdminRegion'] = limit_to_geo_extent(geog_type)

    data = variable.get_values(geogs, time_axis, parent_geog_lvl=geog_type)
    number_format_options = {'style': 'percent'} if use_percent else variable.locale_options
    with connection.cursor() as cursor:
        cursor.execute(f"""DROP VIEW IF EXISTS {view_name}""")
        cursor.execute(f"""DROP TABLE IF EXISTS {table_name}""")
        cursor.execute(f"""CREATE TABLE {table_name} (geoid varchar(63), value numeric)""")
        sql_rows = [f"""('{datum.geog}', {datum.percent if use_percent else datum.value})""" for datum in data]
        cursor.execute(f"""INSERT INTO  {table_name} (geoid, value) VALUES """ + ", ".join(sql_rows))

        cursor.execute(f"""CREATE VIEW {view_name} AS
                                SELECT 
                                    geo.name as geo_name,
                                    geo.geom as the_geom,
                                    geo.geom_webmercator as the_geom_webmercator, 
                                    %(title)s as title,
                                    dat.value::float as value, 
                                    %(number_format_options)s as number_format_options
                                FROM {table_name} dat
                                JOIN ({as_geometry_query(geogs.query)}) geo ON dat.geoid = geo.geoid""",
                       {'title': variable.name, 'number_format_options': json.dumps(number_format_options)})

        # signal tile server to register new view
        # urllib.request.urlopen("http://127.0.0.1:3000/index.json")
