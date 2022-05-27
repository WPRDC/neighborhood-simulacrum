from dataclasses import dataclass, field
from enum import Enum
from typing import Type, Union, Optional, TYPE_CHECKING, Mapping

from django.contrib.gis.db.models.functions import Centroid
from django.contrib.gis.geos import Polygon
from rest_framework.request import Request

from geo.models import Tract, County, BlockGroup, CountySubdivision, AdminRegion, SchoolDistrict, Neighborhood, \
    ZipCodeTabulationArea

if TYPE_CHECKING:
    from indicators.data import Datum
    from indicators.models import Indicator

# Constants
# =-=-=-=-=
GEOG_TYPE_LABEL = 'geogType'
GEOG_ID_LABEL = 'geogID'

GEOG_MODEL_MAPPING = {
    'tract': Tract,
    'county': County,
    'blockGroup': BlockGroup,
    'countySubdivision': CountySubdivision,
    'schoolDistrict': SchoolDistrict,
    'neighborhood': Neighborhood,
    'zcta': ZipCodeTabulationArea
}


# Types/Enums/Etc
# =-=-=-=-=-=-=-=
class ErrorLevel(Enum):
    OK = 0
    EMPTY = 1
    WARNING = 10
    ERROR = 100


@dataclass
class ErrorRecord:
    level: ErrorLevel
    message: Optional[str] = None
    record: Optional[Mapping] = None

    def as_dict(self):
        return {
            'status': self.level.name,
            'level': self.level.value,
            'message': self.message,
            'record': self.record
        }


@dataclass
class DataResponse:
    data: Optional[Union[list['Datum'], dict]]
    dimensions: Optional['Indicator.Dimensions']
    map_options: dict = field(default_factory=dict)
    error: ErrorRecord = ErrorRecord(ErrorLevel.OK)
    warnings: Optional[list[ErrorRecord]] = None

    def as_dict(self):
        return {
            'data': [datum.as_dict() for datum in self.data],
            'dimensions': self.dimensions.response_dict,
            'options': self.map_options,
            'error': self.error.as_dict(),
            'warnings': self.warnings
        }


def get_geog_model(geog_type: str) -> Type[AdminRegion]:
    if geog_type in GEOG_MODEL_MAPPING:
        return GEOG_MODEL_MAPPING[geog_type]
    raise KeyError


def is_geog_data_request(request: Request) -> bool:
    """ Determines if a request should be responded to with calculated indicator data"""
    # for data visualization requests, data can be provided when a geog is defined
    return 'geog' in request.query_params


def get_geog_from_request(request: Request) -> AdminRegion:
    slug = request.query_params.get('geog')
    return AdminRegion.objects \
        .annotate(centroid=Centroid('geom')) \
        .get(slug=slug)


def tile_bbox(z, x, y, srid=3857):
    """
    Returns GEOS Polygon object representing the bbox
    https://github.com/mapbox/postgis-vt-util/blob/master/src/TileBBox.sql
    """
    max_v = 20037508.34
    res = (max_v * 2) / (2 ** z)
    bbox = Polygon.from_bbox((
        -max_v + (x * res),
        max_v - (y * res),
        -max_v + (x * res) + res,
        max_v - (y * res) - res,
    ))
    bbox.srid = 3857
    if srid != 3857:
        bbox.transform(srid)
    return bbox
