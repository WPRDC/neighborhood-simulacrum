from dataclasses import dataclass, field, replace
from typing import Type, List, Optional, TYPE_CHECKING, Collection

from django.db.models import QuerySet, TextChoices
from django.utils.translation import gettext_lazy as _

from geo.models import AdminRegion
from indicators.errors import AggregationError
from profiles.settings import DENOM_DKEY, VALUE_DKEY, GEOG_DKEY, TIME_DKEY

if TYPE_CHECKING:
    from indicators.models import CensusVariable, CKANVariable, Variable


class AggregationMethod(TextChoices):
    NONE = 'NONE', _('None'),
    COUNT = 'COUNT', _('Count'),
    SUM = 'SUM', _('Sum'),
    MEAN = 'AVG', _('Mean'),
    MODE = 'MODE', _('Mode'),
    MAX = 'MAX', _('Maximum'),
    MIN = 'MIN', _('Minimum'),


def aggregate_data(data: Collection[int or float], method: 'AggregationMethod'):
    if method == AggregationMethod.SUM:
        return sum(data)
    if method == AggregationMethod.MEAN:
        return sum(data) / len(data)
    else:
        raise AggregationError(f'{method} not available on ACS or Census values.')


@dataclass
class GeogCollection:
    """
    Collection of `GeogRecords` for geographies of the same type.
    Can and often will contain only one geography
    """
    geog_type: Type[AdminRegion]
    primary_geog: AdminRegion
    records: dict[str, 'GeogRecord'] = field(default_factory=dict)
    _divided: Optional[bool] = None

    @property
    def all_subgeogs(self) -> QuerySet['AdminRegion']:
        all_subgeog_geoids = []
        for geog_record in self.records.values():
            all_subgeog_geoids += [sg.global_geoid for sg in geog_record.subgeogs]
        return AdminRegion.objects.filter(global_geoid__in=all_subgeog_geoids)

    @property
    def is_divided(self):
        if self._divided is None:
            for record in self.records.values():
                if record.is_divided:
                    self._divided = True
                    break
            self._divided = False

        return self._divided


@dataclass
class GeogRecord:
    """
    Dataclass for organizing data when finding and calculating
    values for a variable at a geography across a time_axis
    """
    # the primary geography being examined
    geog: 'AdminRegion'
    # contained geographies of a specific, smaller type whose values can be used in aggregate to describe `geog`
    subgeogs: QuerySet['AdminRegion']

    # a dict mapping subgeog slugs to time_part records time_part slugs to the data for ge
    data_by_subgeog: dict[str, dict[str, 'Datum']] = field(default_factory=dict)
    data_by_time_part: dict[str, dict[str, 'Datum']] = field(default_factory=dict)

    @property
    def geog_type(self) -> str:
        return self.geog.geog_type

    @property
    def geog_class(self) -> Type['AdminRegion']:
        return self.geog.__class__

    @property
    def subgeog_type(self) -> Optional[str]:
        subgeogs = self.subgeogs.all()
        if len(subgeogs):
            return subgeogs[0].geog_type
        return None

    @property
    def subgeog_class(self) -> Optional[Type['AdminRegion']]:
        subgeogs = self.subgeogs.all()
        if len(subgeogs):
            return subgeogs[0].__class__
        return None

    @property
    def is_divided(self) -> bool:
        return self.geog_class != self.subgeog_class

    def get_aggregate_data(self, variable: 'Variable', use_denom: bool) -> dict[str, 'Datum']:
        """
        Generates a representation of the data in this record aggregated across geography so that
        it describes the primary geography `geog` across whatever TimeParts were used to find data for this record.

        :returns: a dict mapping TimePart slugs to Datum for this instance's `geog` at the time.
        """
        # if this is a direct record, then we don't need to perform any aggregation
        if not self.is_divided:
            return self.data_by_subgeog[self.geog.global_geoid]

        # if we need to perform agg_method
        agg_method: AggregationMethod = variable.aggregation_method
        results: dict[str, 'Datum'] = {}
        for time_part_slug, subgeog_record in self.data_by_time_part.items():
            # aggregate values and save them
            data = subgeog_record.values()
            results[time_part_slug] = Datum(
                variable=variable.slug,
                geog=self.geog.global_geoid,
                time=time_part_slug,
                value=aggregate_data([datum.value for datum in data], agg_method),
                # todo: figure out margin of error
                denom=aggregate_data([datum.denom for datum in data], agg_method) if use_denom else None,
            )
        return results

    def add_time_part_records(self, subgeog: AdminRegion, records: dict[str, 'Datum']) -> int:
        """
        Generates and adds TimePart records a dict mapping time_part slugs to data.
        :returns: number of records added.
        """
        count = 0
        if subgeog.global_geoid not in self.data_by_subgeog:
            self.data_by_subgeog[subgeog.global_geoid] = {}

        for time_part_slug, datum in records.items():
            if time_part_slug not in self.data_by_time_part:
                self.data_by_time_part[time_part_slug] = {}

            # keep tract of both hierarchies for now just in case
            self.data_by_subgeog[subgeog.global_geoid][time_part_slug] = datum
            self.data_by_time_part[time_part_slug][subgeog.global_geoid] = datum
            count += 1
        return count


@dataclass
class Datum:
    variable: str
    geog: str
    time: str

    value: Optional[float] = None
    moe: Optional[float] = None

    denom: Optional[float] = None
    percent: Optional[float] = None

    def __post_init__(self):
        if self.denom:
            self.percent = self.value / self.denom

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
        return replace(self, denom=denom_val, percent=(self.value / denom_val))

    def as_dict(self) -> dict:
        return {'variable': self.variable, 'geog': self.geog, 'time': self.time,
                'value': self.value, 'moe': self.moe, 'percent': self.percent, 'denom': self.denom}

    def as_value_dict(self):
        return {'value': self.value, 'moe': self.moe, 'percent': self.percent, 'denom': self.denom}
