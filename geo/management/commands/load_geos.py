import argparse
import os

from django.conf import settings
from django.contrib.gis.gdal import DataSource
from django.contrib.gis.geos import MultiPolygon, Polygon
from django.core.management.base import BaseCommand

import geo
from geo.models import AdminRegion
from maps.util import store_menu_layer
from ..settings import GEOG_SOURCE_MAPPINGS

if hasattr(settings, 'DEFAULT_GEOG_TYPES'):
    DEFAULT_GEOG_TYPES = settings.DEFAULT_GEOG_TYPES
else:
    DEFAULT_GEOG_TYPES = [sc.__name__ for sc in AdminRegion.__subclasses__()]

if hasattr(settings, 'GEOG_SOURCE_MAPPINGS'):
    LAYER_DATA = settings.GEOG_SOURCE_MAPPINGS
else:
    LAYER_DATA: dict = GEOG_SOURCE_MAPPINGS


def load_geography(geog_type_str, base_path=''):
    print('Loading', geog_type_str)

    layer_data = LAYER_DATA[geog_type_str]
    geog_model = getattr(geo.models, geog_type_str)
    ds = DataSource(os.path.join(base_path, layer_data['file_name']))
    field_mapping = layer_data['mapping']
    # limit to first geography in extent.geojson
    extent = DataSource(
        os.path.join(settings.BASE_DIR, 'extent.geojson')
    )[0][0].geom
    for layer in ds:
        layer.spatial_filter = extent
        for feat in layer:
            field_values = {field: feat[feat_field].value
                            for field, feat_field in field_mapping.items()
                            if feat_field in feat.fields}
            if type(feat.geom.geos) == MultiPolygon:
                field_values['geom'] = feat.geom.geos
            elif type(feat.geom.geos) == Polygon:
                field_values['geom'] = MultiPolygon(feat.geom.geos)
            else:
                raise TypeError('Admin regions must be of type POLYGON  or MULTIPOLYGON')
            obj, created = geog_model.objects.get_or_create(**field_values)
            if settings.DEBUG:
                if created:
                    print('✔️', obj.title, 'stored!')
                else:
                    print('⤴️ Skipped', obj.title)
    store_menu_layer(geog_model)

    print('Done!', '\n')


class Command(BaseCommand):
    help = "Load standard geographies"

    def add_arguments(self, parser: argparse.ArgumentParser):
        # Named (optional) arguments
        parser.add_argument(
            '-b',
            '--base-path',
            default=os.path.join(settings.BASE_DIR, 'data', 'geo', '2019'),
            help='Set base path to find source files.'
        )

        parser.add_argument(
            '-G',
            '--geog-types',
            action='append',
            default=[]
        )

    def handle(self, *args, **options):
        for geog_type in options['geog_types']:
            load_geography(geog_type, base_path=options.get('base_path'))
