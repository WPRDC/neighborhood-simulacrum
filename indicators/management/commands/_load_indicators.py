import csv
import json
import os

from django.core.exceptions import ObjectDoesNotExist
from django.template.defaultfilters import slugify

from indicators.models import (Indicator, CensusVariable, CensusSource,
                               Subdomain, CensusVariableSource, Table,
                               VizVariable, DataViz, StaticTimeAxis)

DATA_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    '../../data',
)

CURRENT_INDICATORS = [item.split('.')[0] for item in os.listdir(os.path.join(DATA_DIR, 'indicator_definitions'))]

SOURCES = ['census_2010', 'acs_2017_5yr', ]


def get_slug(indicator_slug, variable_slug, denom_slug, indent):
    middlepart = f'-{denom_slug}-' if int(indent) > 1 else '-'
    r = f'{indicator_slug}{middlepart}{slugify(variable_slug)}'.replace('_', '-')
    return r


def get_or_generate_subdomain(subdomain_title):
    subdomain_slug = slugify(subdomain_title)
    try:
        subdomain = Subdomain.objects.get(slug=subdomain_slug)
    except ObjectDoesNotExist as e:
        subdomain = Subdomain(name=subdomain_title, slug=subdomain_slug)
        subdomain.save()
    return subdomain


def get_or_generate_table(indicator_description, indicator, time_axis):
    try:
        table = Table.objects.get(slug=indicator_description['slug'])
    except ObjectDoesNotExist:
        table = Table(name=indicator_description['name'],
                      slug=indicator_description['slug'],
                      indicator=indicator,
                      time_axis=time_axis)
        table.save()
    return table


def get_or_generate_indicator(indicator_description):
    try:
        indicator = Indicator.objects.get(slug=indicator_description['slug'])
    except ObjectDoesNotExist:
        # add basic fields to indicator
        indicator = Indicator(**{k: v for k, v in indicator_description.items() if k != 'subdomain'})
        indicator.save()
        print(indicator_description['subdomain'])
        # add indicator to its subdomain
        subdomain = get_or_generate_subdomain(indicator_description['subdomain'])
        subdomain.indicators.add(indicator)
        subdomain.save()
    return indicator


def get_year(src_str):
    if src_str == 'census_2010':
        return 2010
    if src_str == 'acs_2017_5yr':
        return 2017


def get_source(src_str):
    if src_str == 'census_2010':
        return CensusSource.objects.get(slug='2010-decennial-census')
    if src_str == 'acs_2017_5yr':
        return CensusSource.objects.get(slug='2017-acs-5yr')


def load():
    # clean house
    Indicator.objects.all().delete()
    DataViz.objects.all().delete()
    CensusVariable.objects.all().delete()
    CensusVariableSource.objects.all().delete()

    for indicator_name in CURRENT_INDICATORS:
        desc_file = os.path.join(DATA_DIR, 'indicator_definitions', f'{indicator_name}.json')
        data_file = os.path.join(DATA_DIR, 'indicator_data', f'{indicator_name}.csv')

        with open(desc_file) as f:
            indicator_description = json.load(f)
            ind_slug = indicator_description['slug']

        # create indicator
        indicator = get_or_generate_indicator(indicator_description)

        # handle variables
        with open(data_file) as f:
            years = set()
            dr = csv.DictReader(f)
            i = 0
            for row in dr:
                # add basic fields
                cur_var = CensusVariable(
                    name=row['title'],
                    slug=get_slug(ind_slug, row['name'], row['denom'], row['indent']),
                    depth=row['indent'],
                )
                cur_var.save()
                time_axis_slug = 'most-recent-acs-year'
                # link variable to sources through CensusVariableSource
                for source in SOURCES:
                    if source in row:
                        if source == 'census_2010':
                            time_axis_slug = 'most-recent-census-year-and-most-recent-acs-year'
                        years.add(get_year(source))
                        CensusVariableSource.objects.create(
                            variable=cur_var,
                            source=get_source(source),
                            formula=row[source]
                        )

                cur_var.save()

                # create table if necessary
                time_axis = StaticTimeAxis.objects.get(slug=time_axis_slug)
                table = get_or_generate_table(indicator_description, indicator, time_axis)

                # add variable to table through VizVariable
                VizVariable.objects.create(data_viz=table, variable=cur_var, order=i)
                i += 1
