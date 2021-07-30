from typing import Type, TYPE_CHECKING

from django.db.models import QuerySet

import indicators.models as indicator_models

if TYPE_CHECKING:
    from geo.models import CensusGeography


def all_geogs_in_domain(geog_type: Type['CensusGeography'], domain: {}) -> QuerySet['CensusGeography']:
    return geog_type.objects.filter(geom__coveredby=domain['the_geom'])


def get_population(geog) -> int:
    pop_var = indicator_models.CensusVariable.objects.get(slug='total-population')
    most_recent_time = indicator_models.TimeAxis.objects.get(slug='most-recent-acs-year').time_parts[0]
    return pop_var.get_primary_value(geog, most_recent_time)


def get_kid_population(geog) -> int:
    pop_var = indicator_models.CensusVariable.objects.get(slug='population-under-18')
    most_recent_time = indicator_models.TimeAxis.objects.get(slug='most-recent-acs-year').time_parts[0]
    return pop_var.get_primary_value(geog, most_recent_time)


def get_black_population(geog) -> int:
    pop_var = indicator_models.CensusVariable.objects.get(slug='pop-by-race-black-or-african-american-alone')
    most_recent_time = indicator_models.TimeAxis.objects.get(slug='most-recent-acs-year').time_parts[0]
    return pop_var.get_primary_value(geog, most_recent_time)
