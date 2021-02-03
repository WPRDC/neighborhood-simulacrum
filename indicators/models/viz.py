from typing import TYPE_CHECKING, Optional

import pystache
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import QuerySet, Manager
from django.db.models.signals import m2m_changed
from django.dispatch import receiver

from polymorphic.models import PolymorphicModel

from indicators.helpers import clean_sql
from indicators.models.abstract import Described
from indicators.utils import DataResponse, ErrorResponse, ErrorLevel

if TYPE_CHECKING:
    from indicators.models import Variable
    from geo.models import CensusGeography


class OrderedVariable(models.Model):
    order = models.IntegerField()

    class Meta:
        abstract = True
        ordering = ['order']


class DataViz(PolymorphicModel, Described):
    """ Base class for all Data Presentations """
    vars: Manager['Variable']
    time_axis = models.ForeignKey('TimeAxis', related_name='data_vizes', on_delete=models.CASCADE)
    indicator = models.ForeignKey('Indicator', related_name='data_vizes', on_delete=models.CASCADE)

    @property
    def variables(self) -> QuerySet['Variable']:
        if self.vars:
            return self.vars.all()
        raise AttributeError('Subclasses of DataPresentation must provide their own `vars` ManyToManyField')

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


# ==================
# +  Map
# ==================

class MapLayer(PolymorphicModel, OrderedVariable):
    map = models.ForeignKey('MiniMap', on_delete=models.CASCADE, related_name='map_to_variable')
    variable = models.ForeignKey('Variable', on_delete=models.CASCADE, related_name='variable_to_map')

    # options
    visible = models.BooleanField()
    limit_to_target_geog = models.BooleanField(default=True)

    # mapbox style
    custom_paint = models.JSONField(help_text='https://docs.mapbox.com/help/glossary/layout-paint-property/',
                                    blank=True, null=True)
    custom_layout = models.JSONField(help_text='https://docs.mapbox.com/help/glossary/layout-paint-property/',
                                     blank=True, null=True)

    # properties of the variable limit possible display states
    # variables without a aggregation method can be used for placing markers
    # variables with aggregation methods can be used for styling geographies
    # variables with aggregation methods and "parcel_source"s can be used to style parcels


class ChoroplethLayer(MapLayer):
    # Choropleth of similar places
    # generate sql statement to send to carto with:
    #   * carto table from the places model joined with
    #   * carto table for the variable
    #   * SELECT cartodb_id, the_geom, the_geom_webmercator, {variable.carto_field} FROM {join_statement} WHERE {sql_filter}
    # style properties

    def get_carto_sql(self, geog: 'CensusGeography'):
        return f'SELECT  '

    pass


class ObjectsLayer(MapLayer):
    # Make Map of things in a place
    # for variable in variables
    # place points returned from variable on map - use through relation to specify style

    pass


class ParcelsLayer(MapLayer):
    # Parcels within the place
    # only one variable
    # generate sql statement to send to carto with:
    #   * get parcels within shape of the geography ST_Intersect
    #   * join them with the data from variable
    #   * SELECT cartodb_id, the_geom, the_geom_webmercator, {parcel_id_field}, {variable.carto_field} FROM {join_statement} WHERE {sql_filter}
    pass


class MiniMap(DataViz):
    vars = models.ManyToManyField('Variable', verbose_name='Layers', through=MapLayer)

    # fields = ArrayField(models.CharField(max_length=80), blank=True)
    # geom_field = models.CharField(max_length=40, default="the_geom")
    # paint = models.JSONField(null=True, blank=True)
    # layout = models.JSONField(null=True, blank=True)
    # filter = models.TextField(null=True, blank=True)

    @property
    def layers(self):
        return self.vars.all()

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


# ==================
# +  Table
# ==================

class TableRow(OrderedVariable):
    table = models.ForeignKey('Table', on_delete=models.CASCADE, related_name='table_to_variable')
    variable = models.ForeignKey('Variable', on_delete=models.CASCADE, related_name='variable_to_table')

    class Meta:
        unique_together = ('table', 'variable', 'order',)


class Table(DataViz):
    vars = models.ManyToManyField('Variable', verbose_name='Rows', through=TableRow)
    transpose = models.BooleanField(default=False)
    show_percent = models.BooleanField(default=True)

    @property
    def variables(self):
        return self.vars.order_by('variable_to_table')

    def get_table_data(self, geog: 'CensusGeography') -> DataResponse:
        data = []
        error: ErrorResponse
        if self.can_handle_geography(geog):
            for variable in self.variables.order_by('variable_to_table'):
                data.append(variable.get_table_row(self, geog))
            error = ErrorResponse(level=ErrorLevel.OK, message=None)
        else:
            error = ErrorResponse(level=ErrorLevel.EMPTY, message=f'This Table is not available for {geog.name}.')

        return DataResponse(data=data, error=error)

    def get_viz_data(self, geog: 'CensusGeography') -> DataResponse:
        return self.get_table_data(geog)


# ==================
# +  Charts
# ==================

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

    def get_chart_data(self, region: 'CensusGeography') -> DataResponse:
        raise NotImplementedError('Each type of chart must define how to get chart data.')

    def _get_chart_data(self, region: 'CensusGeography', through: str) -> DataResponse:
        data = []
        error: ErrorResponse
        if self.can_handle_geography(region):
            for variable in self.variables.order_by(through):
                data.append(variable.get_chart_record(self, region))
            error = ErrorResponse(level=ErrorLevel.OK, message=f'This Chart is not available for this {region.name}.')
        else:
            error = ErrorResponse(level=ErrorLevel.EMPTY, message=None)
        return DataResponse(data=data, error=error)

    def get_viz_data(self, geog: 'CensusGeography') -> DataResponse:
        return self.get_chart_data(geog)

    class Meta:
        abstract = True


class BarChartPart(OrderedVariable):
    chart = models.ForeignKey('BarChart', on_delete=models.CASCADE, related_name='bar_chart_to_variable')
    variable = models.ForeignKey('Variable', on_delete=models.CASCADE, related_name='variable_to_bar_chart')

    @property
    def variables(self):
        return self.vars.order_by('variable_to_viz')

    class Meta:
        unique_together = ('chart', 'variable', 'order',)


class BarChart(Chart):
    vars = models.ManyToManyField('Variable', through=BarChartPart)
    layout = models.CharField(
        max_length=10,
        choices=Chart.LAYOUT_CHOICES,
        default=Chart.HORIZONTAL)

    @property
    def variables(self):
        return self.vars.order_by('variable_to_bar_chart')

    def get_chart_data(self, region: 'CensusGeography') -> DataResponse:
        return self._get_chart_data(region, 'variable_to_bar_chart')


class PieChartPart(OrderedVariable):
    chart = models.ForeignKey('PieChart', on_delete=models.CASCADE, related_name='pie_chart_to_variable')
    variable = models.ForeignKey('Variable', on_delete=models.CASCADE, related_name='variable_to_pie_chart')

    class Meta:
        unique_together = ('chart', 'variable', 'order',)


class PieChart(Chart):
    """
    see: http://recharts.org/en-US/api/Pie
    """
    vars = models.ManyToManyField('Variable', through=PieChartPart)

    @property
    def variables(self):
        return self.vars.order_by('variable_to_pie_chart')

    def get_chart_data(self, region: 'CensusGeography') -> DataResponse:
        return self._get_chart_data(region, 'variable_to_pie_chart')


class LineChartPart(OrderedVariable):
    chart = models.ForeignKey('LineChart', on_delete=models.CASCADE, related_name='line_chart_to_variable')
    variable = models.ForeignKey('Variable', on_delete=models.CASCADE, related_name='variable_to_line_chart')

    class Meta:
        unique_together = ('chart', 'variable', 'order',)


class LineChart(Chart):
    """
    """
    vars = models.ManyToManyField('Variable', through=LineChartPart)
    layout = models.CharField(
        max_length=10,
        choices=Chart.LAYOUT_CHOICES,
        default=Chart.HORIZONTAL)

    @property
    def variables(self):
        return self.vars.order_by('variable_to_line_chart')

    def get_chart_data(self, region: 'CensusGeography') -> DataResponse:
        return self._get_chart_data(region, 'variable_to_line_chart')


class PopulationPyramidChartPart(OrderedVariable):
    chart = models.ForeignKey('PopulationPyramidChart', on_delete=models.CASCADE,
                              related_name='population_pyramid_chart_to_variable')
    variable = models.ForeignKey('Variable', on_delete=models.CASCADE,
                                 related_name='variable_to_population_pyramid_chart')

    class Meta:
        unique_together = ('chart', 'variable', 'order',)


class PopulationPyramidChart(Chart):
    vars = models.ManyToManyField('Variable', through=PopulationPyramidChartPart)

    def get_chart_data(self, region: 'CensusGeography') -> DataResponse:
        return self._get_chart_data(region, 'variable_to_population_pyramid_chart')


# ==================
# +  Alphanumeric
# ==================
class Alphanumeric(DataViz):
    class Meta:
        abstract = True


class BigValueVariable(OrderedVariable):
    alphanumeric = models.ForeignKey('BigValue', on_delete=models.CASCADE, related_name='big_value_to_variable')
    variable = models.ForeignKey('Variable', on_delete=models.CASCADE, related_name='variable_to_big_value')

    class Meta:
        unique_together = ('alphanumeric', 'variable', 'order',)


class BigValue(DataViz):
    vars = models.ManyToManyField('Variable', through=BigValueVariable)
    note = models.TextField(blank=True, null=True)

    def get_value_data(self, geog: 'CensusGeography') -> DataResponse:
        data = None
        error: ErrorResponse
        only_time_part = self.time_axis.time_parts[0]
        if self.can_handle_geography(geog):
            for variable in self.variables.order_by('variable_to_big_value'):
                # fixme: this is wasteful since get_table_row is calculating data we don't use
                data = variable.get_table_row(self, geog)[only_time_part.slug]
            error = ErrorResponse(level=ErrorLevel.OK, message=None)
        else:
            error = ErrorResponse(level=ErrorLevel.EMPTY, message=f'This Value is not available for {geog.name}.')

        return DataResponse(data=data, error=error)

    def get_viz_data(self, geog: 'CensusGeography') -> DataResponse:
        return self.get_value_data(geog)


class SentenceVariable(OrderedVariable):
    alphanumeric = models.ForeignKey('Sentence', on_delete=models.CASCADE, related_name='sentence_to_variable')
    variable = models.ForeignKey('Variable', on_delete=models.CASCADE, related_name='variable_to_sentence')

    class Meta:
        unique_together = ('alphanumeric', 'variable', 'order',)


class Sentence(DataViz):
    vars = models.ManyToManyField('Variable', through=SentenceVariable)
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
                    order = SentenceVariable.objects.filter(alphanumeric=self, variable=variable)[0].order
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


@receiver(m2m_changed, sender=DataViz.variables, dispatch_uid="check_var_timing")
def check_var_timing(sender, instance: DataViz, **kwargs):
    for var in instance.vars.all():
        var: 'Variable'
        for time_part in instance.time_axis.time_parts:
            if not var.can_handle_time_part(time_part):
                raise ValidationError(f'{var.slug} is not available in time {time_part.slug}')
