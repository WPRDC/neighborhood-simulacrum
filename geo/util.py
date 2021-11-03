from typing import Type, TYPE_CHECKING

from django.db.models import QuerySet

if TYPE_CHECKING:
    from geo.models import AdminRegion


def all_geogs_in_extent(geog_type: Type['AdminRegion']) -> QuerySet['AdminRegion']:
    return geog_type.objects.filter(in_extent=True)
