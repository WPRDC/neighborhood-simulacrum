from typing import List, Optional

from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from polymorphic.models import PolymorphicModel
from indicators.models.abstract import Described
from dataclasses import dataclass
from dateutil.relativedelta import relativedelta

MAX_COUNT = 100  # stupid large number for steps on an axis.  anything near this size would be impractical.


def m2q(m: int) -> int:
    """
    Convert month(1-index) to quarter(1-index)
    i.e. m2q(jan) is m2q(1) = 1
    """
    return ((m - 1) // 3) + 1


class TimeAxis(PolymorphicModel, Described):
    """ Base class for time axes. """

    @dataclass
    class TimePart(object):
        """ Holds what's necessary to describe one continuous chunk of time """
        slug: str
        name: str
        time_point: timezone.datetime
        time_unit: int

        @property
        def unit_str(self):
            return TimeAxis.UNIT_FIELDS[self.time_unit]

        @property
        def trunc_sql_str(self):
            trunc_field = self.unit_str
            return f""" date_trunc('{trunc_field}', '{self.time_point.isoformat(sep=' ')}'::timestamp) """

        def __hash__(self):
            return hash((self.slug, self.time_point, self.time_unit))

    # If another time unit is added somehow, make sure its value reflects its relative specificity
    # By comparing specificity, we can tell which units can be rolled up into other, larger ones.
    MINUTE = 1
    HOUR = 2
    DAY = 3
    WEEK = 4
    MONTH = 5
    QUARTER = 6
    YEAR = 7

    UNIT_FIELDS = {
        MINUTE: 'minute',
        HOUR: 'hour',
        DAY: 'day',
        WEEK: 'week',
        MONTH: 'month',
        QUARTER: 'quarter',
        YEAR: 'year',
    }

    REAL_TIME_PERIODS = [MINUTE, HOUR, DAY, WEEK]  # based on a set number of milliseconds
    CALENDAR_TIME_PERIODS = [MONTH, QUARTER, YEAR]  # based on values in calendar rep of date

    UNIT_CHOICES = (
        (MINUTE, 'Minutely'),
        (HOUR, 'Hourly'),
        (DAY, 'Daily'),
        (WEEK, 'Weekly'),
        (MONTH, 'Monthly'),
        (QUARTER, 'Quarterly'),
        (YEAR, 'Yearly'),
    )

    unit = models.IntegerField(choices=UNIT_CHOICES)

    _time_parts: Optional[list[TimePart]] = None

    @property
    def time_points(self) -> List[timezone.datetime]:
        return []

    @property
    def time_parts(self):
        if self._time_parts:
            return self._time_parts
        self._time_parts = [TimeAxis.TimePart(slug=self._get_slug_for_time_point(time_point),
                                              name=self._get_name_for_time_point(time_point),
                                              time_point=time_point,
                                              time_unit=self.unit) for time_point in self.time_points]
        return self._time_parts

    @staticmethod
    def from_time_parts(time_parts: list[TimePart]) -> 'TimeAxis':
        t = TimeAxis(unit=time_parts[0].time_unit)
        t._time_parts = time_parts
        t.slug = '-'.join(sorted([tp.slug for tp in time_parts]))
        t.name = f'Custom Time Axis ({t.slug})'
        return t

    def _get_slug_for_time_point(self, time_point: timezone.datetime):
        if self.unit == self.QUARTER:
            return f'{self.slug}:Q{m2q(time_point.month)}'
        date_part = self.UNIT_FIELDS[self.unit]
        return f'{self.slug}:{getattr(time_point, date_part)}'

    def _get_name_for_time_point(self, time_point: timezone.datetime):
        if self.unit == self.QUARTER:
            return f'Q{m2q(time_point.month)} {time_point.year}'
        if self.unit == self.MONTH:
            return f'{time_point.month}/{time_point.year}'
        if self.unit == self.YEAR:
            return f'{time_point.year}'
        if self.unit == self.DAY:
            return time_point.date().isoformat()
        if self.unit in [self.HOUR]:
            return time_point.isoformat(sep=' ', timespec='hours') + ':00'
        if self.unit in [self.MINUTE]:
            return time_point.isoformat(sep=' ', timespec='minutes')

    def _get_offset_datetime(self,
                             period: int,
                             ref_date: timezone.datetime,
                             displacement: int) -> timezone.datetime:
        if period == self.QUARTER:
            # no quarters option, but 3 calendar months should suffice if not work 100% of the time
            return ref_date + relativedelta(months=displacement * 3)
        if period in [self.MONTH, self.YEAR]:
            # `relativedelta` follows calendar conventions so we don't have to worry about skipping over a month
            return ref_date + relativedelta(**{self.resolution: displacement})
        else:
            # return the date that is `displacement` resolutions (e.g. -3 weeks) away from our reference date
            return ref_date + timezone.timedelta(**{self.resolution: displacement})


class StaticTimeAxis(TimeAxis):
    """ Time axis"""
    dates = ArrayField(models.DateTimeField())

    @property
    def time_points(self) -> List[timezone.datetime]:
        return self.dates


class StaticConsecutiveTimeAxis(TimeAxis):
    """ """
    start = models.DateTimeField()
    end = models.DateTimeField()
    ticks = models.IntegerField()

    @property
    def time_points(self) -> List[timezone.datetime]:
        count = self.ticks if self.ticks else MAX_COUNT
        start_dt = self.start if self.start else self.end
        end_dt = self.end
        direction = 1 if self.start else -1
        results = []
        for distance in range(0, count):
            next_dt = self._get_offset_datetime(self.resolution, start_dt, distance * direction)
            if start_dt and end_dt and next_dt > end_dt:
                # when start and end are both provided, we need to stop at end_dt
                break
            else:
                results.append(next_dt)
        return results

    def clean(self):
        if not ((self.start and self.end) or
                (self.start and self.ticks) or
                (self.end and self.ticks)):
            raise ValidationError('This axis requires two of the three options to be set.')


class RelativeTimeAxis(TimeAxis):
    DIRECTIONS = ((-1, 'Backward'), (1, 'Forward'))

    start_offset = models.IntegerField(
        help_text='start time will be <this value> * <units> offset from the day its accessed; '
                  'negative to go back in time (e.g. if unit is weeks, use -2 for axis to start '
                  '2 weeks prior to moment of viewing')
    ticks = models.IntegerField(help_text='number of units')
    direction = models.IntegerField(choices=DIRECTIONS, default=-1)

    @property
    def time_points(self) -> List[timezone.datetime]:
        count = self.ticks if self.ticks else MAX_COUNT
        start_dt = self._get_offset_datetime(
            self.unit,
            timezone.now(),
            self.start_offset) if self.start_offset else self.end
        results = [self._get_offset_datetime(self.resolution, start_dt, distance * self.direction)
                   for distance in range(0, count)]

        return results
