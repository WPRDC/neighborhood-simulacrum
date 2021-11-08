import csv
import os
from typing import Type, List

from django.conf import settings
from django.core.management.base import BaseCommand

from geo.models import County, AdminRegion, BlockGroup, Tract, CountySubdivision, Neighborhood

PEDIGREE = {
    County: [Tract, BlockGroup],
    CountySubdivision: [Tract, BlockGroup],
    Tract: [BlockGroup],
    BlockGroup: [],
}


class Command(BaseCommand):
    help = "Find and save subregions for Census geographies."

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        region_type: Type['AdminRegion']
        child_types: List[Type['AdminRegion']]
        # for region_type, child_types in PEDIGREE.items():
        #     print(region_type)
        #     for child_type in child_types:
        #         print('-', child_type)
        #         for geog in region_type.objects.all():
        #             child_geogs = child_type.objects.filter(geom__coveredby=geog.geom)
        #             child_geog_ids = [cg.global_geoid for cg in child_geogs]
        #             geog.sub_regions = {**geog.sub_regions, child_type.geog_type_id: child_geog_ids}
        #             geog.save()
        #             print('--', geog, 'saved')
        # print('\n')
        # print('Neighborhoods')
        hood_file = os.path.join(settings.BASE_DIR, 'data', 'geo_lookups', 'hoods_to_blockgroups.csv')
        with open(hood_file) as f:
            reader = csv.DictReader(f)
            for row in reader:
                hood = Neighborhood.objects.get(name=row['hood'])
                print(hood.title, end=': ')
                bg_ids = row['blockgroups'].split('|')
                print(bg_ids)
                hood.subregions = {BlockGroup.geog_type_id: bg_ids}
                hood.save()

        print('Done!')
