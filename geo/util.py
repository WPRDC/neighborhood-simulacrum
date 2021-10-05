from typing import Type, TYPE_CHECKING

from django.db.models import QuerySet

import indicators.models as indicator_models

if TYPE_CHECKING:
    from geo.models import CensusGeography


def all_geogs_in_domain(geog_type: Type['CensusGeography'], domain: {}) -> QuerySet['CensusGeography']:
    return geog_type.objects.filter(geom__coveredby=domain['the_geom'])
