import dataclasses
import typing
from dataclasses import dataclass
from typing import List
from typing import Optional

from profiles.settings import DENOM_DKEY, VALUE_DKEY, GEOG_DKEY, TIME_DKEY

if typing.TYPE_CHECKING:
    from indicators.models import CensusVariable, CKANVariable


@dataclass
class Datum:
    variable: str
    geog: str
    time: str
    value: Optional[float] = None
    moe: Optional[float] = None
    percent: Optional[float] = None
    denom: Optional[float] = None

    @staticmethod
    def from_census_response_datum(variable: 'CensusVariable', census_datum) -> 'Datum':
        return Datum(
            variable=variable.slug,
            geog=census_datum.get('geog'),
            time=census_datum.get('time'),
            value=census_datum.get('value'),
            moe=census_datum.get('moe'),
            denom=census_datum.get('denom'),
            percent=census_datum.get('percent'), )

    @staticmethod
    def from_census_response_data(variable: 'CensusVariable', census_data: list[dict]) -> List['Datum']:
        return [Datum.from_census_response_datum(variable, census_datum) for census_datum in census_data]

    @staticmethod
    def from_ckan_response_datum(variable: 'CKANVariable', ckan_datum) -> 'Datum':
        denom, percent = None, None
        if DENOM_DKEY in ckan_datum:
            denom = ckan_datum[DENOM_DKEY]
            percent = (ckan_datum[VALUE_DKEY] / ckan_datum[DENOM_DKEY])

        return Datum(variable=variable.slug,
                     geog=ckan_datum[GEOG_DKEY],
                     time=ckan_datum[TIME_DKEY],
                     value=ckan_datum[VALUE_DKEY],
                     denom=denom,
                     percent=percent)

    @staticmethod
    def from_ckan_response_data(variable: 'CKANVariable', ckan_data: list[dict]) -> List['Datum']:
        return [Datum.from_ckan_response_datum(variable, ckan_datum) for ckan_datum in ckan_data]

    def update(self, **kwargs):
        """ Creates new Datum similar to the instance with new values from kwargs """
        return Datum(**{**self.as_dict(), **kwargs})

    def with_denom_val(self, denom_val: Optional[float]):
        """ Merge the denom value and generate the percent """
        return dataclasses.replace(self, denom=denom_val, percent=(self.value / denom_val))

    def as_dict(self):
        return {'variable': self.variable, 'geog': self.geog, 'time': self.time,
                'value': self.value, 'moe': self.moe, 'percent': self.percent, 'denom': self.denom}

    def as_value_dict(self):
        return {'value': self.value, 'moe': self.moe, 'percent': self.percent, 'denom': self.denom}
