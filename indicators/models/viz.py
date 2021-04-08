import itertools
import uuid
from operator import itemgetter
from typing import TYPE_CHECKING, Type

import jenkspy
import pystache

from django.core.cache import cache
from django.conf import settings
from django.contrib.gis.db.models import Union
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import QuerySet, Manager, Value
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.utils.text import slugify
from polymorphic.models import PolymorphicModel
from rest_framework.exceptions import NotFound

from geo.models import BlockGroup, County
from geo.serializers import CensusGeographyDataMapSerializer
from indicators.helpers import clean_sql
from indicators.models.abstract import Described
from indicators.utils import DataResponse, ErrorResponse, ErrorLevel

if TYPE_CHECKING:
    from indicators.models import Variable
    from geo.models import CensusGeography

CARTO_REQUIRED_FIELDS = "cartodb_id, the_geom, the_geom_webmercator"

CACHE_TTL = 60 * 60  # 60 mins

class OrderedVariable(models.Model):
    order = models.IntegerField()

    class Meta:
        abstract = True
        ordering = ['order']


class DataViz(PolymorphicModel, Described):
    GRID_UNITS = (
        ('1', 1),
        ('2', 2),
        ('3', 3),
        ('4', 4),
    )

    DEFAULT_WIDTH: int = 3
    DEFAULT_HEIGHT: int = 2

    """ Base class for all Data Presentations """
    _name: str
    vars: Manager['Variable']
    time_axis = models.ForeignKey('TimeAxis', related_name='data_vizes', on_delete=models.CASCADE)
    indicator = models.ForeignKey('Indicator', related_name='data_vizes', on_delete=models.CASCADE)

    width_override = models.IntegerField(
        help_text='Relative width when displayed in a grid with other data presentations.',
        choices=GRID_UNITS,
        null=True, blank=True)

    height_override = models.IntegerField(
        help_text='Relative height when displayed in a grid with other data presentations.',
        choices=GRID_UNITS,
        null=True, blank=True)

    @property
    def view_height(self):
        return self.height_override or self.DEFAULT_HEIGHT

    @property
    def view_width(self):
        return self.width_override or self.DEFAULT_WIDTH

    @property
    def variables(self) -> QuerySet['Variable']:
        if self.vars:
            return self.vars.annotate(viz_options=Value(self.options, output_field=models.JSONField()))
        raise AttributeError('Subclasses of DataPresentation must provide their own `vars` ManyToManyField')

    @property
    def options(self) -> dict:
        options = {}
        field: models.Field
        for rel_obj in self.vars.through.objects.filter(**{self._name: self}):
            for field in rel_obj._meta.get_fields():
                if not field.is_relation and field.attname != 'id':
                    field_name: str = field.get_attname()
                    options[field_name] = getattr(rel_obj, field_name)
        return options

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
    minimap = models.ForeignKey('MiniMap', on_delete=models.CASCADE, related_name='map_to_variable')
    variable = models.ForeignKey('Variable', on_delete=models.CASCADE, related_name='variable_to_map')

    # options
    visible = models.BooleanField()

    # mapbox style
    custom_paint = models.JSONField(help_text='https://docs.mapbox.com/help/glossary/layout-paint-property/',
                                    blank=True, null=True)
    custom_layout = models.JSONField(help_text='https://docs.mapbox.com/help/glossary/layout-paint-property/',
                                     blank=True, null=True)

    # properties of the variable limit possible display states
    # variables without a aggregation method can be used for placing markers
    # variables with aggregation methods can be used for styling geographies
    # variables with aggregation methods and "parcel_source"s can be used to style parcels

    def options(self, geog_type_str: str, data: dict):
        raise NotImplementedError


class GeogChoroplethMapLayer(MapLayer):
    """
    Map Layer where geographies of the same type are styled based on a variable.

    - choropleths
    - categorical maps for admin regions
    """
    COLORS = ['#fff7fb', '#ece7f2', '#d0d1e6', '#a6bddb', '#74a9cf', '#3690c0', '#0570b0', '#045a8d', '#023858']

    sub_geog = models.ForeignKey(
        'geo.CensusGeography',
        help_text='If provided, this geography will be styled within the target geography.  '
                  'Otherwise, the provided geography will be styled along with others of the same level.',
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )

    def options(self, geog_type_str: str, data: dict):
        id = str(uuid.uuid4())
        host = settings.MAP_HOST
        # todo: make bucket count an option
        values = [feat['properties']['map_value'] for feat in data['features'] if
                  feat['properties']['map_value'] is not None]
        breaks = jenkspy.jenks_breaks(values, nb_class=6)[1:]

        # zip breakpoints with colors
        steps = list(itertools.chain.from_iterable(zip(breaks, self.COLORS[1:len(breaks)])))
        fill_color = ["step", ["get", "mapValue"], self.COLORS[0]] + steps

        source = {
            'id': id,
            'type': 'geojson',
            'data': f"{host}/{geog_type_str}:{self.minimap.id}:{self.variable.id}.geojson"
        }
        layers = [{
            "id": f'{id}/boundary',
            'type': 'line',
            'source': id,
            'layout': {},
            'paint': {
                'line-opacity': 1,
                'line-color': '#000',
            },
        }, {
            "id": f'{id}/fill',
            'type': 'fill',
            'source': id,
            'layout': {},
            'paint': {
                'fill-opacity': 0.4,
                'fill-color': fill_color
            },
        }]

        legendType = 'choropleth'
        legendItems = [{'label': str(breaks[i]), 'marker': self.COLORS[i]} for i in range(len(breaks))]

        interactive_layer_ids = [f'{id}/fill']
        return source, layers, interactive_layer_ids, {'type': legendType, 'items': legendItems}


class ObjectsLayer(MapLayer):
    # Make Map of things in a place
    # for variable in variables
    # place points returned from variable on map - use through relation to specify style
    limit_to_target_geog = models.BooleanField(default=True)

    pass


class ParcelsLayer(MapLayer):
    # Parcels within the place
    # only one variable
    # generate sql statement to send to carto with:
    #   * get parcels within shape of the geography ST_Intersect
    #   * join them with the data from variable
    #   * SELECT cartodb_id, the_geom, the_geom_webmercator, {parcel_id_field}, {variable.carto_field} FROM {join_statement} WHERE {sql_filter}
    limit_to_target_geog = models.BooleanField(default=True)
    pass


class MiniMap(DataViz):
    DEFAULT_HEIGHT = 3
    DEFAULT_WIDTH = 3

    BORDER_LAYER_BASE = {
        "type": "line",
        "paint": {
            "line-color": "#333",
            "line-width": [
                "interpolate",
                ["exponential", 1.51],
                ["zoom"],
                0, 1,
                8, 1,
                16, 14
            ]
        },
    }
    _name = 'minimap'
    vars = models.ManyToManyField('Variable', verbose_name='Layers', through=MapLayer)

    @property
    def view_height(self):
        return self.height_override or self.DEFAULT_HEIGHT

    @property
    def view_width(self):
        return self.width_override or self.DEFAULT_WIDTH

    @property
    def layers(self):
        return self.vars.all()

    @property
    def unfiltered_sql(self):
        return f"SELECT {self.fields.join(', ')} FROM {self.carto_table}"

    def get_sql_for_geog(self, geog: 'CensusGeography') -> str:
        # noinspection SqlResolve
        sql = f"""
            SELECT {', '.join(self.fields)} , {self.geom_field}, the_geom_webmercator
            FROM {self.carto_table}
            WHERE ST_Intersects({self.geom_field}, ({geog.carto_geom_sql}))
            """
        if self.filter:
            sql += f""" AND {self.filter}"""

        return clean_sql(sql)

    def _get_map_data(self, geog_type: Type['CensusGeography'], variable: 'Variable') -> dict:
        """
        returns geojson dict for t
        """
        if geog_type == BlockGroup:
            # todo: actually handle this error, then this case
            raise NotFound

        cache_key = f'{self.slug}{variable.slug}@{geog_type.TYPE}'
        cached_geojson = cache.get(cache_key)
        if cached_geojson:
            return cached_geojson
        serializer_context = {'data': variable.get_layer_data(self, geog_type)}

        domain = County.objects \
            .filter(common_geoid__in=settings.AVAILABLE_COUNTIES_IDS) \
            .aggregate(the_geom=Union('geom'))

        geogs: QuerySet['CensusGeography'] = geog_type.objects.filter(geom__coveredby=domain['the_geom'])
        geojson = CensusGeographyDataMapSerializer(geogs, many=True, context=serializer_context).data
        cache.set(cache_key, geojson, CACHE_TTL)
        return geojson

    def get_viz_data(self, geog: 'CensusGeography') -> DataResponse:
        """ Collects and returns the data for this presentation at the `geog` provided

        Cross-geography presentations will cached. keyed in part by `type(geog)`
        as the data returned is the same for any target geog of the same type
        """
        sources: [dict] = []
        layers: [dict] = []
        map_options: dict = {}
        legend_options: [dict] = []
        interactive_layer_ids: [str] = []

        highlight_id = slugify(geog.name)
        highlight_source = {
            'id': f'{highlight_id}',
            'type': 'geojson',
            'data': geog.simple_geojson,
        }
        highlight_layer = {
            'id': f'{highlight_id}/highlight',
            'source': f'{highlight_id}',
            **self.BORDER_LAYER_BASE
        }
        for var in self.vars.all():
            geojson = self._get_map_data(type(geog), var)
            layer: MapLayer = self.vars.through.objects.get(variable=var, minimap=self)
            source, tmp_layers, interactive_layer_ids, legend_option = layer.options(geog.geog_type, geojson)
            sources.append(source)
            legend_option['title'] = var.name
            legend_options.append(legend_option)
            layers += tmp_layers

        map_options['interactive_layer_ids'] = interactive_layer_ids
        map_options['default_viewport'] = {
            'longitude': geog.geom.centroid.x,
            'latitude': geog.geom.centroid.y,
            'zoom': geog.base_zoom
        }

        sources.append(highlight_source)
        layers.append(highlight_layer)

        return DataResponse(
            data={'sources': sources, 'layers': layers, 'map_options': map_options, 'legends': legend_options},
            error=ErrorResponse(level=ErrorLevel.OK))

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
    # todo: calculate height based on number of columns
    DEFAULT_WIDTH = 2
    DEFAULT_HEIGHT = 2

    _name = 'table'
    vars = models.ManyToManyField('Variable', verbose_name='Rows', through=TableRow)
    transpose = models.BooleanField(default=False)
    show_percent = models.BooleanField(default=True)

    @property
    def view_height(self):
        return (len(self.vars.all()) // 5) + 4

    @property
    def view_width(self):
        return self.width_override or self.DEFAULT_WIDTH

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
    DEFAULT_WIDTH = 3
    DEFAULT_HEIGHT = 2

    _name = 'chart'
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

    across_geogs = models.BooleanField(
        help_text='Check if you want this chart to compare the statistic across geographies instead of across time',
        default=False)

    @property
    def view_height(self):
        return self.height_override or self.DEFAULT_HEIGHT

    @property
    def view_width(self):
        return self.width_override or self.DEFAULT_WIDTH

    def get_chart_data(self, geog: 'CensusGeography') -> DataResponse:
        raise NotImplementedError('Each type of chart must define how to get chart data.')

    def _get_data_across_geogs(self, geog_type: Type['CensusGeography'], variable: 'Variable') -> []:
        cache_key = f'{self.slug}{variable.slug}@{geog_type.TYPE}'
        cached_data = cache.get(cache_key)
        if cached_data:
            return cached_data

        data = []
        domain = County.objects \
            .filter(common_geoid__in=settings.AVAILABLE_COUNTIES_IDS) \
            .aggregate(the_geom=Union('geom'))

        for geog in geog_type.objects.filter(geom__coveredby=domain['the_geom']):
            data.append(variable.get_chart_record(self, geog, by_geog=True))

        time_slug = self.time_axis.time_parts[0].slug
        sorted_data = sorted([d for d in data if time_slug in d], key=itemgetter(time_slug))
        cache.set(cache_key, sorted_data, CACHE_TTL)
        return sorted_data

    def _get_data_across_variables(self, geog: 'CensusGeography', variables: QuerySet['Variable']) -> []:
        data = []
        for variable in variables:
            data.append(variable.get_chart_record(self, geog))
        return data

    def _get_chart_data(self, geog: 'CensusGeography', through: str) -> DataResponse:
        data = []
        error: ErrorResponse
        variables = self.variables.order_by(through)

        if self.can_handle_geography(geog):
            if self.across_geogs:
                data = self._get_data_across_geogs(type(geog), variables[0])
            else:
                data = self._get_data_across_variables(geog, variables)
            error = ErrorResponse(level=ErrorLevel.OK,
                                  message=f'This Chart is not available for this {geog.name}.')
        else:
            error = ErrorResponse(level=ErrorLevel.EMPTY, message=None)
        return DataResponse(data=data, error=error)

    def get_viz_data(self, geog: 'CensusGeography') -> DataResponse:
        return self.get_chart_data(geog)

    class Meta:
        abstract = True


class BarChartPart(OrderedVariable):
    NONE = None
    HIGHLIGHT = 'HI'
    SUBTLE = 'SU'
    AVERAGE = 'AVG'
    STYLE_CHOICES = ((NONE, 'None'), (HIGHLIGHT, 'Highlight'), (SUBTLE, 'Subtle'), (AVERAGE, 'Avg/Mean'))
    chart = models.ForeignKey('BarChart', on_delete=models.CASCADE, related_name='bar_chart_to_variable')
    variable = models.ForeignKey('Variable', on_delete=models.CASCADE, related_name='variable_to_bar_chart')
    style = models.CharField(verbose_name='Special Style', max_length=4, choices=STYLE_CHOICES,
                             default=None, null=True, blank=True)

    class Meta:
        unique_together = ('chart', 'variable', 'order',)


class BarChart(Chart):
    DEFAULT_WIDTH = 5

    vars = models.ManyToManyField('Variable', through=BarChartPart)
    layout = models.CharField(
        max_length=10,
        choices=Chart.LAYOUT_CHOICES,
        default=Chart.HORIZONTAL)

    @property
    def variables(self):
        return self.vars.order_by('variable_to_bar_chart')

    def get_chart_data(self, geog: 'CensusGeography') -> DataResponse:
        return self._get_chart_data(geog, 'variable_to_bar_chart')


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

    def get_chart_data(self, geog: 'CensusGeography') -> DataResponse:
        return self._get_chart_data(geog, 'variable_to_pie_chart')


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

    def get_chart_data(self, geog: 'CensusGeography') -> DataResponse:
        return self._get_chart_data(geog, 'variable_to_line_chart')


class PopulationPyramidChartPart(OrderedVariable):
    chart = models.ForeignKey('PopulationPyramidChart', on_delete=models.CASCADE,
                              related_name='population_pyramid_chart_to_variable')
    variable = models.ForeignKey('Variable', on_delete=models.CASCADE,
                                 related_name='variable_to_population_pyramid_chart')

    class Meta:
        unique_together = ('chart', 'variable', 'order',)


class PopulationPyramidChart(Chart):
    vars = models.ManyToManyField('Variable', through=PopulationPyramidChartPart)

    def get_chart_data(self, geog: 'CensusGeography') -> DataResponse:
        return self._get_chart_data(geog, 'variable_to_population_pyramid_chart')


# ==================
# +  Alphanumeric
# ==================
class Alphanumeric(DataViz):
    _name = 'alphanumeric'

    class Meta:
        abstract = True


class BigValueVariable(OrderedVariable):
    alphanumeric = models.ForeignKey('BigValue', on_delete=models.CASCADE, related_name='big_value_to_variable')
    variable = models.ForeignKey('Variable', on_delete=models.CASCADE, related_name='variable_to_big_value')

    class Meta:
        unique_together = ('alphanumeric', 'variable', 'order',)


class BigValue(Alphanumeric):
    DEFAULT_WIDTH = 2
    vars = models.ManyToManyField('Variable', through=BigValueVariable)
    note = models.TextField(blank=True, null=True)

    def get_value_data(self, geog: 'CensusGeography') -> DataResponse:
        data = []
        error: ErrorResponse
        only_time_part = self.time_axis.time_parts[0]
        if self.can_handle_geography(geog):
            for variable in self.variables.order_by('variable_to_big_value'):
                tmp_data = variable.get_table_row(self, geog)[only_time_part.slug]

                if tmp_data is None or tmp_data['v'] is None:
                    # todo: better error reporting
                    error = ErrorResponse(level=ErrorLevel.EMPTY,
                                          message=f'This Value is not available for {geog.name}.')
                    data = None
                else:
                    # todo: add options
                    data.append({'v': tmp_data['v'], 'options': None})
                    error = ErrorResponse(level=ErrorLevel.OK, message=None)

        else:
            error = ErrorResponse(level=ErrorLevel.EMPTY, message=f'This Value is not available for {geog.name}.')

        return DataResponse(data=data, error=error)

    def get_viz_data(self, geog: 'CensusGeography') -> DataResponse:
        return self.get_value_data(geog)

    @property
    def view_width(self):
        return self.width_override or self.DEFAULT_WIDTH


class SentenceVariable(OrderedVariable):
    alphanumeric = models.ForeignKey('Sentence', on_delete=models.CASCADE, related_name='sentence_to_variable')
    variable = models.ForeignKey('Variable', on_delete=models.CASCADE, related_name='variable_to_sentence')

    class Meta:
        unique_together = ('alphanumeric', 'variable', 'order',)


class Sentence(Alphanumeric):
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
            error = ErrorResponse(level=ErrorLevel.EMPTY,
                                  message=f'This Sentence is not available for {geog.name}.')

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
