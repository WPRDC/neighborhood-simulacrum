import json
import urllib.request
from typing import TYPE_CHECKING, Type
from urllib.error import URLError

from django.conf import settings
from django.db import connection

from indicators.data import GeogCollection
from indicators.models.data import CachedIndicatorData

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
    return f'maps.{geog_type.geog_type_id.lower()}'


# noinspection SqlAmbiguousColumn ,SqlResolve
def store_map_data(
        map_slug: str,
        geog_collection: 'GeogCollection',
        time_axis: 'TimeAxis',
        variable: 'Variable',
        use_percent: bool
):
    number_format_options = {'style': 'percent'} if use_percent else variable.number_format_options
    with connection.cursor() as cursor:
        cursor.execute(f"""DROP VIEW IF EXISTS maps."{map_slug}" """)

        base_geography_subquery = as_geometry_query(geog_collection.geog_type.objects.filter(in_extent=True).query)
        time_hashes = ','.join([f"'{tp.storage_hash}'" for tp in time_axis.time_parts])
        subgeogs = ','.join([f"'{sg.global_geoid}'" for sg in geog_collection.all_subgeogs.all()])

        # query for data
        cursor.execute(
            f"""
            CREATE VIEW maps."{map_slug}" AS
            SELECT geo.slug                  as "geog",
                   geo.name                  as "geogLabel",
            
                   %(time_slug)s             as "time",
                   %(time_name)s             as "timeLabel",
            
                   %(var_slug)s              as "variable",
                   %(var_name)s              as "variableLabel",
                   %(var_abbr)s              as "variableAbbr",
            
                   %(number_format_options)s as "numberFormatOptions",
            
                   geo.geom as "the_geom", 
                   geo.geom_webmercator      as "the_geom_webmercator", 
                   dat.the_value::float      as "value"
            FROM (SELECT cid.geog          as geog_global_geoid,
                         cid.variable      as varaible_slug,
                         cid.time_part_hash,
                         {'(cid."value" / cid."denom")' if use_percent else '(cid."value")'} as "the_value"
                  FROM {CachedIndicatorData._meta.db_table} cid
                  WHERE variable = '{variable.slug}'
                    AND time_part_hash IN ({time_hashes})
                    AND geog IN ({subgeogs})) dat
                     JOIN ({base_geography_subquery}) geo ON dat.geog_global_geoid = geo.global_geoid
            """,
            {
                'title': variable.name,
                'time_slug': time_axis.time_parts[0].slug,
                'time_name': time_axis.time_parts[0].name,
                'var_slug': variable.slug,
                'var_name': variable.name,
                'var_abbr': variable.short_name,
                'number_format_options': json.dumps(number_format_options),
            }
        )

        refresh_tile_index()


def store_menu_layer(geog_type: Type['AdminRegion']):
    """ Creates tables of geographies to be served by tile server for use in menus"""
    print('Adding menu view for', geog_type.geog_type_id)
    view_name = menu_view_name(geog_type)
    view_query = as_tile_server_query(geog_type.objects.filter(in_extent=True).query)

    # todo: make geog menu table with limited, standardized fields

    with connection.cursor() as cursor:
        cursor.execute(f"""DROP VIEW IF EXISTS {view_name}""")
        cursor.execute(f"""CREATE VIEW {view_name} AS {view_query}""")

    print('Menu view added.')

    refresh_tile_index()


def point_symbology(primary_color):
    return [{
        'type': 'circle',
        'paint': {
            'circle-opacity': 0.8,
            'circle-stroke-width': 1,
            'circle-radius': [
                "interpolate",
                ["exponential", 1.11],
                ["zoom"],
                9,
                1,
                22,
                12
            ],
            'circle-color': primary_color,
            'circle-stroke-color': '#000000'
        }
    }]


def polygon_symbology(primary_color):
    return {
        'type': 'fill'
    }