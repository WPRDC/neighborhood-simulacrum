import itertools
import json
import random
import typing
import uuid
from functools import lru_cache

import requests
from ckanapi import RemoteCKAN
from colorfield.fields import ColorField
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.postgres.fields import ArrayField
from django.db import connection
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from jenkspy import jenks_breaks
from polymorphic.models import PolymorphicModel

from context.models import WithTags
from geo.models import AdminRegion
from indicators.data import GeogCollection
from indicators.errors import NotAvailableForGeogError
from maps.color import color_brewer_choices
from maps.util import store_map_data, refresh_tile_index, point_symbology
from profiles.abstract_models import Described, TimeStamped
from profiles.types import CKANResource, CKANPackage

if typing.TYPE_CHECKING:
    from indicators.models.variable import Variable
    from indicators.models.time import TimeAxis

DEFAULT_CHOROPLETH_COLORS = ['#FFF7FB', '#ECE7F2', '#D0D1E6', '#A6BDDB', '#74A9CF',
                             '#3690C0', '#0570B0', '#045A8D', '#023858']

ckan_api = RemoteCKAN(settings.CKAN_HOST, user_agent=settings.USER_AGENT)


def random_color():
    return "#%06x" % random.randint(0, 0xFFFFFF)


class IndicatorLayer(Described, TimeStamped):
    """
    Record of each map stored, one per any geogType-variable-timePart combination.

    When it's made, it is given the name of the table with its data.
    """
    label = models.CharField(max_length=200)
    geog_type_id = models.CharField(max_length=100)  # geog_type_id
    geog_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    variable = models.ForeignKey('indicators.Variable', on_delete=models.CASCADE)
    time_axis = models.ForeignKey('indicators.TimeAxis', on_delete=models.CASCADE)
    number_format_options = models.JSONField(default=dict)
    use_percent = models.BooleanField(default=False)

    _breaks = None

    class Meta:
        unique_together = ('geog_content_type', 'variable', 'time_axis')

    @property
    def database_map_view(self) -> str:
        return f'maps."{self.slug}"'

    @property
    def source(self):
        return self.vector_source

    @property
    def vector_source(self):
        layer_id = self.database_map_view.replace('"', '')
        return {
            'id': self.slug,
            'type': 'vector',
            'url': f"https://api.profiles.wprdc.org/tiles/{layer_id}.json",
        }

    @property
    def geojson_source(self):
        host = "https://api.profiles.wprdc.org/maps/geojson"
        return {
            'id': self.slug,
            'type': 'geojson',
            'data': f"{host}/{self.slug}.geojson"  # todo: figure out how to serve map data
        }

    @property
    def legend(self):
        breaks = self.breaks
        legend_variant = 'scale'
        legend_items = [{'label': breaks[i],
                         'marker': DEFAULT_CHOROPLETH_COLORS[i]} for i in range(len(breaks))]
        return {'label': self.label,
                'number_format_options': {'style': 'percent'} if self.use_percent else self.number_format_options,
                'variant': legend_variant,
                'scale': legend_items}

    @property
    def layers(self):
        _id = self.slug
        breaks = self.breaks
        # zip breakpoints with colors
        steps = list(itertools.chain.from_iterable(zip(breaks, DEFAULT_CHOROPLETH_COLORS[1:len(breaks)])))
        source_layer = self.database_map_view.replace('"', '')
        fill_color = ["step", ["get", "value"], DEFAULT_CHOROPLETH_COLORS[0]] + steps
        return [{
            "id": f'{_id}/boundary',
            'type': 'line',
            'source': _id,
            'source-layer': source_layer,
            'layout': {},
            'paint': {
                'line-opacity': 1,
                'line-color': '#000',
            },
        }, {
            "id": f'{_id}/fill',
            'type': 'fill',
            'source': _id,
            'source-layer': source_layer,
            'layout': {},
            'paint': {
                'fill-opacity': 0.8,
                'fill-color': fill_color
            },
        }]

    @property
    def interactive_layer_ids(self):
        return [f'{self.slug}/fill']

    @property
    def breaks(self):
        # todo: handle custom bucket counts
        try:
            if not self._breaks:
                values = [feat['properties']['value'] for feat in self.as_geojson()['features'] if
                          feat['properties']['value'] is not None]
                self._breaks = jenks_breaks(values, nb_class=min(len(values), 6))[0:]
            return self._breaks
        except ValueError as e:
            raise NotAvailableForGeogError(
                f'This map is not available for geography Level: {self.geog_content_type.name}.'
            )

    def as_geojson(self) -> dict:
        """ Return [geojson](https://geojson.org) representation of the map """
        query = f"""SELECT json_build_object(
                                    'type', 'FeatureCollection',
                                    'features', json_agg(ST_AsGeoJSON(v.*)::json)) 
                    FROM (
                        SELECT 
                            ST_ForceRHR(ST_Transform(the_geom, 4326)) as geom, 
                            "value" as map_value, 
                            "value" 
                        FROM {self.database_map_view}
                    ) v;
        """

        with connection.cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchone()[0]

    @staticmethod
    def get_or_create_updated_map(geog_collection: 'GeogCollection',
                                  time_axis: 'TimeAxis',
                                  variable: 'Variable',
                                  use_percent: bool) -> 'IndicatorLayer':
        """
        Returns a Map object associated with the args.

        If a Map isn't already registered, the data is collected and a new map is created and returned.
        If it exists but the data is out of date, new data will be collected and an updated map is returned.
        Otherwise, the existing map is returned.

        TODO:  have this get the full collection if only one record is sent.
        TODO: cache the data returned so we can use it for the histogram.

        """
        geog_ctype: ContentType = ContentType.objects.get_for_model(geog_collection.geog_type)
        try:
            # check if we already have map data
            return IndicatorLayer.objects.get(geog_content_type=geog_ctype, variable=variable, time_axis=time_axis)
            # todo: do some freshness checks - and update data if necessary
        except IndicatorLayer.DoesNotExist:
            # if not, we need to get the data and register it with a new map record
            geog_type_id = geog_collection.geog_type.geog_type_id
            geog_type_title = geog_collection.geog_type.geog_type_title
            slug = 'dl_' + str(uuid.uuid4()).replace('-', '_')

            # create data table
            store_map_data(slug, geog_collection, time_axis, variable, use_percent)

            return IndicatorLayer.objects.create(
                name=f"{variable.name} across {geog_type_title}",
                label=f"{variable.name}",
                slug=slug,
                geog_type_id=geog_type_id,
                time_axis=time_axis,
                geog_content_type=geog_ctype,
                variable=variable,
                use_percent=use_percent,
                number_format_options=variable.number_format_options
            )

    def get_map_options(self):
        return self.source, self.layers, self.interactive_layer_ids, self.legend

    def __str__(self):
        return self.name


class MapLayer(PolymorphicModel, Described, WithTags, TimeStamped):
    """ Shared fields across different types of map layers """
    POINT = 'Point'
    LINE_STRING = 'LineString'
    POLYGON = 'Polygon'
    MULTI_POINT = 'MultiPoint'
    MULTI_LINE_STRING = 'MultiLineString'
    MULTI_POLYGON = 'MultiPolygon'

    GEOG_TYPE_CHOICES = (
        (POINT, 'Point'),
        (LINE_STRING, 'LineString'),
        (POLYGON, 'Polygon'),
        (MULTI_POINT, 'MultiPoint'),
        (MULTI_LINE_STRING, 'MultiLineString'),
        (MULTI_POLYGON, 'MultiPolygon'),
    )

    geog_type = models.CharField(max_length=15, choices=GEOG_TYPE_CHOICES)

    source_override = models.JSONField(null=True, blank=True)
    layers_override = models.JSONField(null=True, blank=True)

    point_paint_override = models.JSONField(null=True, blank=True)
    point_layout_override = models.JSONField(null=True, blank=True)

    fill_paint_override = models.JSONField(null=True, blank=True)
    fill_layout_override = models.JSONField(null=True, blank=True)

    line_paint_override = models.JSONField(null=True, blank=True)
    line_layout_override = models.JSONField(null=True, blank=True)

    primary_color = ColorField(default=random_color)
    color_scale = models.CharField(max_length=100, choices=color_brewer_choices)

    @property
    def tile_json(self):
        return f'{settings.TILE_SERVER_URL}/{settings.MAPS_SCHEMA}.{self.slug}.json'

    @property
    def source(self):
        raise NotImplementedError

    @property
    def layers(self):
        raise NotImplementedError

    @property
    def legend(self):
        raise NotImplementedError


class CKANLayer(MapLayer):
    """ Map layers from mappable resources in the CKAN datastore """
    resource_id = models.UUIDField()
    id_field = models.CharField(
        max_length=100,
        default=settings.CKAN_DEFAULT_ID_FIELD,
        null=True,
        blank=True,
    )
    geom_field = models.CharField(
        max_length=100,
        default=settings.CKAN_DEFAULT_GEOM_FIELD,
        null=True,
        blank=True,
    )
    geom_webmercator_field = models.CharField(
        max_length=100,
        default=settings.CKAN_DEFAULT_GEOM_WEBMERCATOR_FIELD,
        null=True,
        blank=True,
    )
    image_field = models.CharField(
        max_length=100,
        help_text='Leave blank if no image',
        null=True,
        blank=True,
    )

    category_field = models.CharField(
        max_length=100,
        help_text='Leave blank to not color by category',
        null=True,
        blank=True
    )

    categories_override = ArrayField(
        models.CharField(max_length=100),
        null=True,
        blank=True,
    )

    sql_override = models.TextField(null=True, blank=True)
    srid = models.IntegerField(verbose_name='SRID', default=4326)

    @property
    @lru_cache
    def resource(self) -> CKANResource:
        return ckan_api.action.resource_show(id=str(self.resource_id))

    @property
    @lru_cache
    def package(self) -> CKANPackage:
        return ckan_api.action.package_show(id=str(self.resource['package_id']))

    @property
    def source(self):
        return {
            'id': self.slug,
            'type': 'vector',
            'url': f'{settings.TILE_SERVER_URL}/{self.table_name}.json',

        }

    @property
    def layers(self) -> list[dict]:
        if 'Point' in self.geog_type:
            return self.point_symbology
        if 'Polygon' in self.geog_type:
            return self.polygon_symbology
        else:
            return []

    @property
    def legend(self):
        pass

    def get_arc_rest_service(self) -> CKANResource:
        for resource in self.package['resources']:
            if resource['name'] == 'Esri Rest API':
                return resource
        return None

    @property
    def fields(self) -> dict[str, str]:
        resource_id = str(self.resource_id)
        if self.resource['format'].lower() == 'geojson':
            rest_service_resource = self.get_arc_rest_service()
            if rest_service_resource:
                data = requests.get(rest_service_resource['url'] + '?f=pjson').json()
                return {field['name'].lower(): field['actualType'] for field in data['fields']}
            csv_resource = self.get_sibling_csv()
            if csv_resource:
                resource_id = csv_resource['id']
            else:
                resource_id = None
        if resource_id:
            return ckan_api.action.datastore_info(id=resource_id)['schema']

    @property
    def table_name(self):
        return f'{settings.MAPS_SCHEMA}.ckan_{self.slug.replace("-", "_")}'

    def make_base_layer_props(self, name):
        return {
            'id': f'{self.slug}/{name}',
            'source': self.slug,
            'source-layer': self.table_name,
        }

    @property
    def point_symbology(self):
        return [{
            **self.make_base_layer_props('circle'),
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
                'circle-color': self.primary_color,
                'circle-stroke-color': '#000000',
                **(self.point_paint_override or {})
            },
            'layout': {
                **(self.point_layout_override or {})
            }
        }]

    @property
    def polygon_symbology(self):
        return [
            {
                **self.make_base_layer_props('fill'),
                'type': 'fill',
                'paint': {
                    'fill-color': self.primary_color,
                    'fill-opacity': 0.7,
                    **(self.fill_paint_override or {})
                },
                'layout': {
                    **(self.fill_layout_override or {})
                }
            },
            {
                **self.make_base_layer_props('line'),
                'type': 'line',
                'paint': {
                    **(self.line_paint_override or {})
                },
                'layout': {
                    **(self.line_layout_override or {})
                }
            }
        ]

    def get_sibling_csv(self) -> typing.Optional[CKANResource]:
        resource: CKANResource
        for resource in self.package['resources']:
            # fixme: maybe we can tag these as this is prone to break in the future
            if resource["datastore_active"] and 'data dictionary' not in resource['name'].lower():
                return resource
        return None

    def retrieve_geojson(self):
        if self.resource['format'].lower() == 'geojson':
            r = requests.get(self.resource['url'])
            data = r.json()
            return data
        raise Exception('Only works for geojson resources')

    def save_tile_table(self):
        """
        Creates materialized view using foreign data wrapper to datastore.

        If the resource is not in the datastore, data will be extracted and stored in profiles,
        otherwise a view will be made with data in the datastore foreign data wrapper
        (https://www.postgresql.org/docs/current/postgres-fdw.html)

        """
        # add geom fields to set of fields
        fields = {
            **self.fields,
            # self.geom_field: f'geometry({self.geog_type},{self.srid})',
            self.geom_webmercator_field: f'geometry({self.geog_type},3857)'
        }
        table_name = self.table_name

        if self.resource['format'].lower() == 'geojson':
            # extract data and store in profiles db
            with connection.cursor() as cursor:
                # (re)create empty table
                cursor.execute(f"""DROP TABLE IF EXISTS {table_name} """)
                cursor.execute(f"""
                    CREATE TABLE {table_name} (
                        {', '.join([f'{field.lower()} {dtype}' for field, dtype in fields.items()])}
                    )
                """)

                # read data from features of geojson and load into the fresh table
                features = self.retrieve_geojson()['features']
                value_lines = [
                    f"({', '.join([sql_wrap(feature['properties'][k]) for k in feature['properties']])}" +
                    f''', ST_Transform(ST_SetSRID(ST_GeomFromGeoJSON('{json.dumps(feature["geometry"])}'), 4326), 3857))'''

                    for feature in features
                    if feature['geometry']
                ]
                query = f"""
                    INSERT INTO {table_name} ({', '.join([field.lower() for field in fields.keys()])})
                    VALUES
                    {', '.join(value_lines)}
                """
                cursor.execute(query)

        elif self.sql_override:
            query = f"""
            CREATE MATERIALIZED VIEW {table_name} AS
            {self.sql_override}
            """
            with connection.cursor() as cursor:
                cursor.execute(f'DROP MATERIALIZED VIEW IF EXISTS {table_name};')
                cursor.execute(query)


        else:
            property_fields = [f'"{field}"' for field in self.fields.keys()
                               if field not in [
                                   settings.CKAN_DEFAULT_ID_FIELD,
                                   settings.CKAN_DEFAULT_GEOM_FIELD,
                                   settings.CKAN_DEFAULT_GEOM_WEBMERCATOR_FIELD,
                                   'id', 'geom', 'geom_webmercator'
                               ]]

            query = f"""
            CREATE MATERIALIZED VIEW {table_name} AS
            SELECT 
                "{self.id_field}" as id,
                {', '.join(property_fields)}, 
                "{self.geom_webmercator_field}" as geom_webmercator
            FROM datastore."{self.resource_id}"
            """
            with connection.cursor() as cursor:
                cursor.execute(f'DROP MATERIALIZED VIEW IF EXISTS {table_name};')
                cursor.execute(query)

        refresh_tile_index()

    def post_save(self):
        self.save_tile_table()


def sql_wrap(n) -> str:
    if type(n) is str:
        f"'{n}'"
    return f'{n}'


@receiver(post_save, sender=CKANLayer)
def create_tiles_after_save(sender, instance: CKANLayer, **kwargs):
    instance.post_save()
