from django.core.management.base import BaseCommand
from django.utils import timezone

from geo.models import County, CensusGeography, Tract
from indicators.models import CensusValue, CensusVariable, CensusSource

REGIONAL_COUNTIES = (
    'Allegheny',
    'Washington',
    'Butler',
    'Armstrong',
    'Westmoreland',
    'Beaver'
    'Fayette',
    'Greene',
    'Indiana',
    'Lawrence',
)

CHUNK_SIZE = 40

current_counties = County.objects.filter(name__in=REGIONAL_COUNTIES, statefp=42)


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def save_data(data, region):
    for table, value in data.items():
        if table in ['state', 'county', 'tract', 'block group']:
            continue
        CensusValue.objects.create(region=region, census_table=table, value=value)


def get_census_data(tables, region: CensusGeography):
    source = CensusSource.objects.get(dataset='CEN')
    return source.get_data(tables, region)


def get_acs_data(tables, region: CensusGeography):
    source = CensusSource.objects.get(dataset='ACS5')
    return source.get_data(tables, region)


def get_and_store_data(acs_table, cen_table, region):
    for chunk in chunks(list(acs_table), CHUNK_SIZE):
        acs_data = get_acs_data(chunk, region)
        print(acs_data)
        save_data(acs_data[0], region)
    print('---')
    cen_data = get_census_data(list(cen_table), region)
    print(cen_data, '\n------\n\n')
    save_data(cen_data[0], region)


class Command(BaseCommand):
    help = "Load generated indicators"

    def add_arguments(self, parser):
        # todo: add arguments that map to the `load_census_boundaries.run()` ones
        pass

    def handle(self, *args, **options):
        """
        Gather all of the census tables used across all CensusVariables
          For each region:
            For each chunk of census tables   //(size tbd)
             Make api call with the chunk for the region
             create census values for each (table, region) pair (table_i, region) for i in len(table)
        """
        cen_2010_tables = set()
        acs_2017_tables = set()

        for census_variable in CensusVariable.objects.all():
            for table in census_variable.get_formula_parts_at_time_point(timezone.datetime(2010, 1, 1)):
                cen_2010_tables.add(table)
            for table in census_variable.get_formula_parts_at_time_point(timezone.datetime(2017, 1, 1)):
                acs_2017_tables.add(table)

        print('Removing old census values')
        CensusValue.objects.all().delete()
        for county in current_counties:
            print('County: ', county)
            get_and_store_data(acs_2017_tables, cen_2010_tables, county)

        for tract in Tract.objects.filter(statefp=42, countyfp=County.objects.get(geoid='42003')):
            get_and_store_data(acs_2017_tables, cen_2010_tables, tract)
