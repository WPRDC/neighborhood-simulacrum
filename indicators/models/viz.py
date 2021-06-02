import itertools
import re
import uuid
from typing import TYPE_CHECKING, Type, Optional

import jenkspy
import pystache
from django.conf import settings
from django.contrib.gis.geos import GEOSGeometry
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import QuerySet, Manager, F
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.utils.text import slugify
from polymorphic.models import PolymorphicModel

from geo.serializers import CensusGeographyDataMapSerializer
from indicators.errors import DataRetrievalError, EmptyResultsError
from indicators.models.abstract import Described
from indicators.models.source import Source
from indicators.utils import DataResponse, ErrorResponse, ErrorLevel, limit_to_geo_extent

if TYPE_CHECKING:
    from indicators.models.variable import Variable
    from geo.models import CensusGeography

CARTO_REQUIRED_FIELDS = "cartodb_id, the_geom, the_geom_webmercator"

CACHE_TTL = 60 * 60  # 60 mins

pattern = re.compile(r'(?<!^)(?=[A-Z])')


class VizVariable(models.Model):
    """ Common fields and methods for all variables attached to data vizes """
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
        """ Public property for accessing the variables int he viz. """
        variable_to_viz = f'variable_to_{self.ref_name}'
        if self.vars:
            return self.vars.order_by(variable_to_viz)
        raise AttributeError('Subclasses of DataPresentation must provide their own `vars` ManyToManyField')

    @property
    def options(self) -> dict:
        return {}

    @property
    def viz_type(self) -> str:
        return self.__class__.__qualname__

    @property
    def ref_name(self) -> str:
        """ The snake case string used to reference this model in related names. """
        name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', self.viz_type)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()

    @property
    def sources(self) -> QuerySet['Source']:
        """ Queryset representing the set of sources attached to all variables in this viz. """
        source_ids = set()
        variable: Variable
        for variable in self.variables:
            var_source_ids = [s.id for s in variable.sources.all()]
            for var_source_id in var_source_ids:
                source_ids.add(var_source_id)
        return Source.objects.filter(pk__in=list(source_ids))

    def can_handle_geography(self, geog: 'CensusGeography') -> bool:
        """
        Returns `True` if the variables in this visualization and, in turn, their sources, work
        with the supplied geography.
        :param geog:
        :return:
        """
        var: 'Variable'
        for var in self.vars.all():
            if not var.can_handle_geography(geog):
                return False
        return True

    def can_handle_geographies(self, geogs: QuerySet['CensusGeography']) -> bool:
        for geog in geogs.all():
            if not self.can_handle_geography(geog):
                return False
        return True

    def get_geog_queryset(self, geog: 'CensusGeography') -> tuple[Optional[QuerySet['CensusGeography']], bool]:
        """
        Returns a queryset representing the the minimum set of geographies to for which data can be
        aggregated to represent `geog` and a bool representing whether or not child geogs are used.

        `None` is returned if no such non-empty set exists.

        :param geog: teh geography being examined
        :return: Queryset of geographies to for which data can be aggregated to represent `geog`; None if an emtpy set.
        """
        # check how geog works for this viz
        # does it work directly for the goeg?
        if self.can_handle_geography(geog):
            return type(geog).objects.filter(pk=geog.pk), False

        # does it work as an aggregate over a smaller geog?
        for child_geog_model in geog.child_geog_models:
            child_geogs = child_geog_model.objects.filter(mini_geom__coveredby=geog.big_geom)

            if self.can_handle_geographies(child_geogs):
                return child_geogs, True

        return None, False

    def get_viz_data(self, geog: 'CensusGeography') -> DataResponse:
        """
        Returns a `DataResponse` object with the viz's data at `geog`.

        All the nitty-gritty work of spatial, temporal and categorical harmonization happens here. Any inability to
        harmonize should return an empty dataset and an error response explaining what went wrong (e.g. not available
        for 'geog' because of privacy reasons)

        This method is the primary interface to request data.
        :param geog: the geography being examined
        :return: DataResponse with data and error information
        """
        # get queryset representing geog though itself or child geogs
        geogs, use_agg = self.get_geog_queryset(geog)
        parent_geog_lvl = type(geog) if use_agg else None
        data, options, error = None, None, ErrorResponse(ErrorLevel.OK)
        try:
            if geogs:
                data = self._get_viz_data(geogs, parent_geog_lvl=parent_geog_lvl)
                options = self._get_viz_options(geog)
            else:
                error = ErrorResponse(level=ErrorLevel.EMPTY,
                                      message=f'This visualization is not available for {geog.name}.')
        except DataRetrievalError as e:
            error = e.error_response
        finally:
            return DataResponse(data, options, error)

    def _get_viz_data(self, geogs: QuerySet['CensusGeography'],
                      parent_geog_lvl: Optional[Type['CensusGeography']] = None) -> list[dict]:
        """
        Gets a representation of data for the viz.

        If representing the data as a list of records doesn't make sense for the visualization (e.g. maps),
        this method can be overridden.

        :param geogs:
        :return:
        """
        data: list[dict] = []
        for variable in self.variables:
            data += [datum.as_dict() for datum in
                     variable.get_values(geogs, self.time_axis, parent_geog_lvl=parent_geog_lvl)]

        return data

    def _get_viz_options(self, geog: 'CensusGeography') -> Optional[dict]:
        return {}

    class Meta:
        verbose_name = "Data Visualization"
        verbose_name_plural = "Data Visualizations"


# ==================
# +  Map
# ==================
class MiniMap(DataViz):
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
    vars = models.ManyToManyField('Variable', verbose_name='Layers', through='MapLayer')
    use_percent = models.BooleanField(default=False)

    @property
    def layers(self):
        return self.vars.all()

    def get_map_data_geojson(self, geog_type: Type['CensusGeography'], variable: 'Variable') -> dict:
        """
        returns geojson dict with data for `variable` and the geogs of type `geog_type`
        """
        geogs = limit_to_geo_extent(geog_type) # todo: also figure out parent geog
        data = variable.get_values(geogs, self.time_axis, parent_geog_lvl=geog_type)

        locale_options = {'style': 'percent'} if self.use_percent else variable.locale_options
        serializer_context = {'data': data, 'percent': self.use_percent, 'locale_options': locale_options}

        geojson = CensusGeographyDataMapSerializer(geogs, many=True, context=serializer_context).data
        return geojson

    def _get_viz_data(self, geogs: QuerySet['CensusGeography'],
                      parent_geog_lvl: Optional[Type['CensusGeography']] = None) -> list[dict]:
        return []  # map data is stored in geojson that is served elsewhere

    def _get_viz_options(self, geog: 'CensusGeography', parent_geog_lvl=None) -> dict:
        """
        Collects and returns the data for this presentation at the `geog` provided

        Cross-geography presentations will cached. keyed in part by `type(geog)`
        as the data returned is the same for any target geog of the same type
        """
        sources: [dict] = []
        layers: [dict] = []
        interactive_layer_ids: [str] = []
        legend_options: [dict] = []
        locale_options = {'style': 'percent'} if self.use_percent else self.variables[0].locale_options

        for var in self.vars.all():
            # for each variable/layer, get its data geojson, style and options
            geojson = self.get_map_data_geojson(type(geog), var)
            layer: MapLayer = self.vars.through.objects.get(variable=var, viz=self)
            source, tmp_layers, interactive_layer_ids, legend_option = layer.get_map_options(geog.geog_type, geojson)
            sources.append(source)
            legend_option['title'] = var.name
            legend_option['locale_options'] = locale_options
            legend_options.append(legend_option)
            layers += tmp_layers

        map_options: dict = {
            'interactive_layer_ids': interactive_layer_ids,
            'default_viewport': {
                'longitude': geog.geom.centroid.x,
                'latitude': geog.geom.centroid.y,
                'zoom': geog.base_zoom - 3
            }
        }

        # for highlighting current geog
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
        sources.append(highlight_source)
        layers.append(highlight_layer)

        return {'sources': sources, 'layers': layers, 'legends': legend_options,
                'map_options': map_options, 'locale_options': locale_options}

    def __str__(self):
        return self.name


class MapLayer(PolymorphicModel, VizVariable):
    """ Base class for map layers """
    viz = models.ForeignKey('MiniMap', on_delete=models.CASCADE, related_name='mini_map_to_variable')
    variable = models.ForeignKey('Variable', on_delete=models.CASCADE, related_name='variable_to_mini_map')

    # options
    visible = models.BooleanField()

    # mapbox style
    custom_paint = models.JSONField(help_text='https://docs.mapbox.com/help/glossary/layout-paint-property/',
                                    blank=True, null=True)
    custom_layout = models.JSONField(help_text='https://docs.mapbox.com/help/glossary/layout-paint-property/',
                                     blank=True, null=True)

    def get_map_options(self, geog_type_str: str, data: dict):
        raise NotImplementedError


class GeogChoroplethMapLayer(MapLayer):
    """
    Map Layer where geographies of the same type are styled based on a variable.

    - choropleths
    - categorical maps for admin regions
    """
    COLORS = ['#FFF7FB', '#ECE7F2', '#D0D1E6', '#A6BDDB', '#74A9CF', '#3690C0', '#0570B0', '#045A8D', '#023858']

    sub_geog = models.ForeignKey(
        'geo.CensusGeography',
        help_text='If provided, this geography will be styled within the target geography. '
                  'Otherwise, the provided geography will be styled along with others of the same level.',
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )

    def get_map_options(self, geog_type_str: str, data: dict):
        _id = str(uuid.uuid4())
        host = settings.MAP_HOST
        # todo: make bucket count an option
        values = [feat['properties']['map_value'] for feat in data['features'] if
                  feat['properties']['map_value'] is not None]

        breaks = jenkspy.jenks_breaks(values, nb_class=min(len(values), 6))[0:]

        # zip breakpoints with colors
        steps = list(itertools.chain.from_iterable(zip(breaks, self.COLORS[1:len(breaks)])))
        fill_color = ["step", ["get", "mapValue"], self.COLORS[0]] + steps

        source = {
            'id': _id,
            'type': 'geojson',
            'data': f"{host}/{geog_type_str}:{self.viz.id}:{self.variable.id}.geojson"
        }
        layers = [{
            "id": f'{_id}/boundary',
            'type': 'line',
            'source': _id,
            'layout': {},
            'paint': {
                'line-opacity': 1,
                'line-color': '#000',
            },
        }, {
            "id": f'{_id}/fill',
            'type': 'fill',
            'source': _id,
            'layout': {},
            'paint': {
                'fill-opacity': 0.8,
                'fill-color': fill_color
            },
        }]

        legend_type = 'choropleth'
        legend_items = [{'label': breaks[i],
                         'marker': self.COLORS[i]} for i in range(len(breaks))]

        interactive_layer_ids = [f'{_id}/fill']
        return source, layers, interactive_layer_ids, {'type': legend_type, 'items': legend_items}


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
    #   * SELECT cartodb_id, the_geom, the_geom_webmercator, {parcel_id_field},
    #   {variable.carto_field} FROM {join_statement} WHERE {sql_filter}
    limit_to_target_geog = models.BooleanField(default=True)
    pass


# ==================
# +  Table
# ==================
class Table(DataViz):
    vars = models.ManyToManyField('Variable', verbose_name='Rows', through='TableRow')
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

    def _get_viz_data(self, geogs: QuerySet['CensusGeography'],
                      parent_geog_lvl: Optional[Type['CensusGeography']] = None) -> list[dict]:
        """ Gets data for each variable across time """
        data_check = []
        results = []
        for variable in self.variables:
            var_data = variable.get_values(geogs, self.time_axis, parent_geog_lvl=parent_geog_lvl)
            data_check += var_data
            time_data = {datum.time: datum.as_value_dict() for datum in var_data}
            results.append({'variable': variable.slug, **time_data})
        if not data_check:
            raise EmptyResultsError('Data not available.')
        return results

    def _get_viz_options(self, geog: 'CensusGeography') -> Optional[dict]:
        columns = [{"Header": '', "accessor": 'variable'}, ] + \
                  [{"Header": tp.name, "accessor": tp.slug} for tp in self.time_axis.time_parts]
        return {'transpose': self.transpose, 'show_percent': self.show_percent, 'columns': columns}


class TableRow(VizVariable):
    viz = models.ForeignKey('Table', on_delete=models.CASCADE, related_name='table_to_variable')
    variable = models.ForeignKey('Variable', on_delete=models.CASCADE, related_name='variable_to_table')

    class Meta:
        unique_together = ('viz', 'variable', 'order',)


# ==================
# +  Charts
# ==================
class Chart(DataViz):
    """
    Abstract base class for charts
    """
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
    vars = models.ManyToManyField('Variable', verbose_name='Rows', through='ChartPart')
    legend_type = models.CharField(max_length=10, choices=LEGEND_TYPE_CHOICES, default='circle')

    across_geogs = models.BooleanField(
        help_text='Check if you want this chart to compare the statistic across geographies instead of across time',
        default=False)

    @property
    def options(self) -> dict:
        return {'across_geogs': self.across_geogs}

    def _get_viz_options(self, geog: 'CensusGeography') -> Optional[dict]:
        return {'legend_type': self.legend_type, 'across_geogs': self.across_geogs}


class ChartPart(VizVariable):
    viz = models.ForeignKey('Chart', on_delete=models.CASCADE, related_name='chart_to_variable')
    variable = models.ForeignKey('Variable', on_delete=models.CASCADE, related_name='variable_to_chart')

    class Meta:
        unique_together = ('viz', 'variable', 'order',)


# ==================
# +  Alphanumeric
# ==================
class Alphanumeric(DataViz):
    class Meta:
        abstract = True


class BigValueVariable(VizVariable):
    viz = models.ForeignKey('BigValue', on_delete=models.CASCADE, related_name='big_value_to_variable')
    variable = models.ForeignKey('Variable', on_delete=models.CASCADE, related_name='variable_to_big_value')

    class Meta:
        unique_together = ('viz', 'variable', 'order',)


class BigValue(Alphanumeric):
    PLAIN = 'PLN'
    FRACTION = 'FRN'
    PERCENT = 'PCT'
    BOTH = 'BTH'
    FORMAT_CHOICES = (
        (PLAIN, "Plain"),
        (FRACTION, "Approximate, human friendly, fraction over denominator."),
        (PERCENT, "Percent of denominator"),
        (BOTH, "Number and Fraction"),
    )
    vars = models.ManyToManyField('Variable', through=BigValueVariable)
    note = models.TextField(blank=True, null=True)
    format = models.TextField(max_length=3, choices=FORMAT_CHOICES, default=PLAIN,
                              help_text="Only use percent for numbers with denominators. "
                                        "Variables with 'percent' as a unit should use 'Plain'")

    @property
    def view_width(self):
        return self.width_override or self.DEFAULT_WIDTH


class SentenceVariable(VizVariable):
    viz = models.ForeignKey('Sentence', on_delete=models.CASCADE, related_name='sentence_to_variable')
    variable = models.ForeignKey('Variable', on_delete=models.CASCADE, related_name='variable_to_sentence')

    class Meta:
        unique_together = ('viz', 'variable', 'order',)


class Sentence(Alphanumeric):
    vars = models.ManyToManyField('Variable', through=SentenceVariable)
    text = models.TextField(
        help_text='To place a value in your sentence, use {order}. e.g. "There are {1} cats and {2} dogs in town."')

    def get_text_data(self, geog: 'CensusGeography') -> DataResponse:
        data = ''
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


@receiver(m2m_changed, sender=DataViz.variables, dispatch_uid="check_var_timing")
def check_var_timing(_, instance: DataViz, **kwargs):
    for var in instance.vars.all():
        var: 'Variable'
        for time_part in instance.time_axis.time_parts:
            if not var.can_handle_time_part(time_part):
                raise ValidationError(f'{var.slug} is not available in time {time_part.slug}')
