from typing import TYPE_CHECKING
import re

import pystache
from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.db.models import QuerySet
from django.db.models.signals import m2m_changed
from django.dispatch import receiver

from polymorphic.models import PolymorphicModel

from indicators.helpers import clean_sql
from indicators.models.abstract import Described
from indicators.utils import DataResponse, ErrorResponse, ErrorLevel

if TYPE_CHECKING:
    from indicators.models import Variable
    from geo.models import CensusGeography


class DataViz(PolymorphicModel, Described):
    time_axis = models.ForeignKey('TimeAxis', related_name='data_vizes', on_delete=models.CASCADE)
    vars = models.ManyToManyField('Variable', through='VizVariable')
    indicator = models.ForeignKey('Indicator', related_name='data_vizes', on_delete=models.CASCADE)

    @property
    def variables(self) -> QuerySet['Variable']:
        return self.vars.order_by('variable_to_viz')

    def can_handle_geography(self, geog: 'CensusGeography') -> bool:
        var: 'Variable'
        for var in self.vars.all():
            if var.can_handle_geography(geog):
                return True
        return False

    def get_viz_data(self, geog: 'CensusGeography') -> DataResponse:
        return DataResponse(data=None,
                            error=ErrorResponse(level=ErrorLevel.ERROR,
                                                message='Data Viz has no data getter.'))

    class Meta:
        verbose_name = "Data Visualization"
        verbose_name_plural = "Data Visualizations"


class VizVariable(models.Model):
    data_viz = models.ForeignKey('DataViz', on_delete=models.CASCADE, related_name='viz_to_variable')
    variable = models.ForeignKey('Variable', on_delete=models.CASCADE, related_name='variable_to_viz')
    order = models.IntegerField()

    class Meta:
        verbose_name = "Visualization Variable"
        verbose_name_plural = "Visualization Variables"
        ordering = ['order']
        unique_together = ('data_viz', 'variable', 'order',)


class MiniMap(DataViz):
    LAYER_TYPES = (
        ('background', 'background'),
        ('fill', 'fill'),
        ('line', 'line'),
        ('symbol', 'symbol'),
        ('raster', 'raster'),
        ('circle', 'circle'),
        ('fill - extrusion', 'fill - extrusion'),
        ('heatmap', 'heatmap'),
        ('hillshade', 'hillshade')
    )
    layer_type = models.CharField(max_length=16, choices=LAYER_TYPES, default='line')
    carto_table = models.CharField(max_length=80)
    fields = ArrayField(models.CharField(max_length=80), blank=True)
    geom_field = models.CharField(max_length=40, default="the_geom")
    paint = models.JSONField(null=True, blank=True)
    layout = models.JSONField(null=True, blank=True)
    filter = models.TextField(null=True, blank=True)

    @property
    def unfiltered_sql(self):
        return f"SELECT {self.fields.join(', ')} FROM {self.carto_table}"

    def get_sql_for_region(self, region: 'CensusGeography') -> str:
        # noinspection SqlResolve
        sql = f"""
                SELECT {', '.join(self.fields)} , {self.geom_field}, the_geom_webmercator
                FROM {self.carto_table}
                WHERE ST_Intersects({self.geom_field}, ({region.carto_geom_sql}))
                """
        if self.filter:
            sql += f""" AND {self.filter}"""

        return clean_sql(sql)

    def __str__(self):
        return self.name


class Table(DataViz):
    """
                | t1  | t2
        cat A   | data      | data
        cat B   | data      | data
    """
    transpose = models.BooleanField(default=False)
    show_percent = models.BooleanField(default=True)

    @property
    def variables(self):
        return self.vars.order_by('variable_to_viz')

    def get_table_data(self, geog: 'CensusGeography') -> DataResponse:
        data = []
        error: ErrorResponse
        if self.can_handle_geography(geog):
            for variable in self.variables.order_by('variable_to_viz'):
                data.append(variable.get_table_row(self, geog))
            error = ErrorResponse(level=ErrorLevel.OK, message=None)
        else:
            error = ErrorResponse(level=ErrorLevel.EMPTY, message=f'This Table is not available for {geog.name}.')

        return DataResponse(data=data, error=error)

    def get_viz_data(self, geog: 'CensusGeography') -> DataResponse:
        return self.get_table_data(geog)


class BigValue(DataViz):
    note = models.TextField(blank=True, null=True)

    def get_value_data(self, geog: 'CensusGeography') -> DataResponse:
        data = None
        error: ErrorResponse
        only_time_part = self.time_axis.time_parts[0]
        if self.can_handle_geography(geog):
            for variable in self.variables.order_by('variable_to_viz'):
                # fixme: this is wasteful since get_table_row is calculating data we don't use
                data = variable.get_table_row(self, geog)[only_time_part.slug]
            error = ErrorResponse(level=ErrorLevel.OK, message=None)
        else:
            error = ErrorResponse(level=ErrorLevel.EMPTY, message=f'This Value is not available for {geog.name}.')

        return DataResponse(data=data, error=error)

    def get_viz_data(self, geog: 'CensusGeography') -> DataResponse:
        return self.get_value_data(geog)


class Sentence(DataViz):
    text = models.TextField(
        help_text='To place a value in your sentence, use {order}. e.g. "There are {1} cats and {2} dogs in town."')

    def get_text_data(self, geog: 'CensusGeography') -> DataResponse:
        data = ''
        fields = {}
        error: ErrorResponse
        only_time_part = self.time_axis.time_parts[0]

        if self.can_handle_geography(geog):
            fields = {'geo': geog.title, }
            try:
                for variable in self.vars.all():
                    order = VizVariable.objects.filter(data_viz=self, variable=variable)[0].order
                    val = variable.get_table_row(self, geog)[only_time_part.slug]['v']
                    fields[f'v{order}'] = f"<strong>{val}</strong>"
                    denoms = variable.denominators.all()
                    if denoms:
                        d_val = variable.get_proportional_datum(geog, only_time_part, denoms[0])
                        fields[f'v{order}d'] = f"{d_val:.2%}"
                data = pystache.render(self.text, fields)
                error = ErrorResponse(level=ErrorLevel.OK, message=None)
            except Exception as e:
                error = ErrorResponse(level=ErrorLevel.ERROR, message=str(e))
        else:
            error = ErrorResponse(level=ErrorLevel.EMPTY, message=f'This Sentence is not available for {geog.name}.')

        return DataResponse(data=data, error=error)

    def get_viz_data(self, geog: 'CensusGeography') -> DataResponse:
        return self.get_text_data(geog)


class Chart(DataViz):
    """
    Abstract base class for charts
    """
    HORIZONTAL = 'horizontal'
    VERTICAL = 'vertical'
    LAYOUT_CHOICES = ((HORIZONTAL, 'Horizontal'), (VERTICAL, 'Vertical'))

    LINE = 'line'
    SQUARE = 'square'
    RECT = 'rect'
    CIRCLE = 'circle'
    CROSS = 'cross'
    DIAMOND = 'diamond'
    STAR = 'star'
    TRIANGLE = 'triangle'
    WYE = 'wye'
    NONE = 'none'
    LEGEND_TYPE_CHOICES = (
        (LINE, 'Line'),
        (SQUARE, 'Square'),
        (RECT, 'Rectangle'),
        (CIRCLE, 'Circle'),
        (CROSS, 'Cross'),
        (DIAMOND, 'Diamond'),
        (STAR, 'Star'),
        (TRIANGLE, 'Triangle'),
        (WYE, 'Wye'),
        (NONE, 'None'),
    )
    legendType = models.CharField(max_length=10, choices=LEGEND_TYPE_CHOICES, default='circle')

    @property
    def variables(self):
        return self.vars.order_by('variable_to_viz')

    def get_chart_data(self, region: 'CensusGeography') -> DataResponse:
        data = []
        error: ErrorResponse
        if self.can_handle_geography(region):
            for variable in self.variables.order_by('variable_to_viz'):
                data.append(variable.get_chart_record(self, region))
            error = ErrorResponse(level=ErrorLevel.OK, message=f'This Chart is not available for this {region.name}.')
        else:
            error = ErrorResponse(level=ErrorLevel.EMPTY, message=None)
        return DataResponse(data=data, error=error)

    def get_viz_data(self, geog: 'CensusGeography') -> DataResponse:
        return self.get_chart_data(geog)

    class Meta:
        abstract = True


class BarChart(Chart):
    layout = models.CharField(
        max_length=10,
        choices=Chart.LAYOUT_CHOICES,
        default=Chart.HORIZONTAL)


class PieChart(Chart):
    """
    see: http://recharts.org/en-US/api/Pie
    """
    pass


class LineChart(Chart):
    """
    """
    layout = models.CharField(
        max_length=10,
        choices=Chart.LAYOUT_CHOICES,
        default=Chart.HORIZONTAL)


class PopulationPyramidChart(Chart):
    pass


@receiver(m2m_changed, sender=DataViz.vars.through, dispatch_uid="check_var_timing")
def check_var_timing(sender, instance: DataViz, **kwargs):
    for var in instance.vars.all():
        var: 'Variable'
        for time_part in instance.time_axis.time_parts:
            if not var.can_handle_time_part(time_part):
                raise ValidationError(f'{var.slug} is not available in time {time_part.slug}')
