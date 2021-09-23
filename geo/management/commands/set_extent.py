from django.conf import settings
from django.contrib.gis.db.models import Union as GeoUnion
from django.core.management.base import BaseCommand

from geo.models import Geography, County


class Command(BaseCommand):
    help = "Mark geographies that are within the extent of the application. " \
           "Saves on performing the same complicated queries over and over again later on."

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        extent = County.objects \
            .filter(common_geoid__in=settings.AVAILABLE_COUNTIES_IDS) \
            .aggregate(the_geom=GeoUnion('geom'))
        Geography.objects.filter(geom__coveredby=extent['the_geom']).update(in_extent=True)
