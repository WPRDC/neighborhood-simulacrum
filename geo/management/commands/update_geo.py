from django.contrib.gis.geos import GEOSGeometry, MultiPolygon, Polygon
from django.core.management.base import BaseCommand
from django.contrib.gis.gdal import DataSource
from geo import models

class Command(BaseCommand):
    help = "Load standard geographies"

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        data_source = DataSource('data/geo/2019/pgh_neighborhoods/pgh_neighborhoods.shp')
        layer = data_source[0]

        for feature in layer:
            geoid = feature.get('geoid10')
            print(geoid)
            geog = models.Neighborhood.objects.get(common_geoid=geoid)
            print(geog)
            geom = feature.geom
            new_geom = GEOSGeometry(geom.wkt)
            if type(new_geom) == Polygon:
                new_geom = MultiPolygon(new_geom)
            print(new_geom)
            print('############\n\n')
            geog.geom = new_geom
            geog.save()
