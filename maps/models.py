import itertools
import typing
import uuid
from typing import List

from django.contrib.contenttypes.models import ContentType
from django.db import connection
from django.db import models
from jenkspy import jenks_breaks

from geo.models import AdminRegion
from indicators.data import GeogCollection
from indicators.errors import NotAvailableForGeogError
from maps.util import store_map_data
from profiles.abstract_models import Described, TimeStamped

if typing.TYPE_CHECKING:
    from indicators.models.variable import Variable
    from indicators.models.time import TimeAxis


DEFAULT_CHOROPLETH_COLORS = ['#FFF7FB', '#ECE7F2', '#D0D1E6', '#A6BDDB', '#74A9CF',
                             '#3690C0', '#0570B0', '#045A8D', '#023858']


class DataLayer(Described, TimeStamped):
    """
    Record of each map stored, one per any geogType-variable-timePart combination.

    When it's made, it is given the name of the table with its data.
    """
    label = models.CharField(max_length=200)
    geog_type_id = models.CharField(max_length=100)  # geog_type_id
    geog_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    variable = models.ForeignKey('indicators.Variable', on_delete=models.CASCADE)
    time_axis = models.ForeignKey('indicators.TimeAxis', on_delete=models.CASCADE)
    number_format_options = models.JSONField(default=dict)
    use_percent = models.BooleanField(default=False)

    _breaks = None

    class Meta:
        unique_together = ('geog_content_type', 'variable', 'time_axis')

    @property
    def database_data_table(self) -> str:
        return f'maps.t_{self.slug}'

    @property
    def database_map_view(self) -> str:
        return f'maps.v_{self.slug}'

    @property
    def values(self) -> List[dict]:
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT * FROM {self.database_data_table}")
            headers = ['geoid', 'value']
            return [
                dict(zip(headers, row))
                for row in cursor.fetchall()
            ]

    @property
    def source(self):
        return self.vector_source

    @property
    def vector_source(self):
        layer_id = self.database_map_view.replace('"', '')
        return {
            'id': self.slug,
            'type': 'vector',
            'url': f"https://api.profiles.wprdc.org/tiles/{layer_id}.json",
        }

    @property
    def geojson_source(self):
        host = "https://api.profiles.wprdc.org/maps/geojson"
        return {
            'id': self.slug,
            'type': 'geojson',
            'data': f"{host}/{self.slug}.geojson"  # todo: figure out how to serve map data
        }

    @property
    def legend(self):
        breaks = self.breaks
        legend_variant = 'scale'
        legend_items = [{'label': breaks[i],
                         'marker': DEFAULT_CHOROPLETH_COLORS[i]} for i in range(len(breaks))]
        return {'label': self.label,
                'locale_options': self.number_format_options,  # fixme: remove when we can
                'number_format_options': {'style': 'percent'} if self.use_percent else self.number_format_options,
                'variant': legend_variant,
                'scale': legend_items}

    @property
    def layers(self):
        _id = self.slug
        breaks = self.breaks
        # zip breakpoints with colors
        steps = list(itertools.chain.from_iterable(zip(breaks, DEFAULT_CHOROPLETH_COLORS[1:len(breaks)])))
        source_layer = self.database_map_view.replace('"', '')
        fill_color = ["step", ["get", "value"], DEFAULT_CHOROPLETH_COLORS[0]] + steps
        return [{
            "id": f'{_id}/boundary',
            'type': 'line',
            'source': _id,
            'source-layer': source_layer,
            'layout': {},
            'paint': {
                'line-opacity': 1,
                'line-color': '#000',
            },
        }, {
            "id": f'{_id}/fill',
            'type': 'fill',
            'source': _id,
            'source-layer': source_layer,
            'layout': {},
            'paint': {
                'fill-opacity': 0.8,
                'fill-color': fill_color
            },
        }]

    @property
    def interactive_layer_ids(self):
        return [f'{self.slug}/fill']

    @property
    def breaks(self):
        # todo: handle custom bucket counts
        try:
            if not self._breaks:
                values = [feat['properties']['value'] for feat in self.as_geojson()['features'] if
                          feat['properties']['value'] is not None]
                self._breaks = jenks_breaks(values, nb_class=min(len(values), 6))[0:]
            return self._breaks
        except ValueError as e:
            raise NotAvailableForGeogError(
                f'This map is not available for geography Level: {self.geog_content_type.name}.'
            )

    def as_geojson(self) -> dict:
        """ Return [geojson](https://geojson.org) representation of the map """
        query = f"""SELECT json_build_object(
                                    'type', 'FeatureCollection',
                                    'features', json_agg(ST_AsGeoJSON(v.*)::json)) 
                    FROM (
                        SELECT 
                            ST_ForceRHR(ST_Transform(the_geom, 4326)) as geom, 
                            "value" as map_value, 
                            "value" 
                        FROM {self.database_map_view}
                    ) v;
        """

        #             'id',
        #             'title',
        #             'geom',
        #             'map_value',
        #             'number_format_options'

        print(query)
        with connection.cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchone()[0]

    @staticmethod
    def get_or_create_updated_map(geog_collection: 'GeogCollection',
                                  time_axis: 'TimeAxis',
                                  variable: 'Variable',
                                  use_percent: bool) -> 'DataLayer':
        """
        Returns a Map object associated with the args.

        If a Map isn't already registered, the data is collected and a new map is created and returned.
        If it exists but the data is out of date, new data will be collected and an updated map is returned.
        Otherwise the existing map is returned.
        """
        geog_ctype: ContentType = ContentType.objects.get_for_model(geog_collection.geog_type)
        try:
            # check if we already have map data
            return DataLayer.objects.get(geog_content_type=geog_ctype, variable=variable, time_axis=time_axis)
            # todo: do some freshness checks - and update data if necessary
        except DataLayer.DoesNotExist:
            # if not, we need to get the data and register it with a new map record
            geog_type_id = geog_collection.geog_type.geog_type_id
            geog_type_title = geog_collection.geog_type.geog_type_title
            slug = str(uuid.uuid4()).replace('-', '_')

            # create data table
            store_map_data(slug, geog_collection, time_axis, variable, use_percent)

            return DataLayer.objects.create(
                name=f"{variable.name} across {geog_type_title}",
                label=f"{variable.name}",
                slug=slug,
                geog_type_id=geog_type_id,
                time_axis=time_axis,
                geog_content_type=geog_ctype,
                variable=variable,
                use_percent=use_percent,
                number_format_options=variable.locale_options
            )

    def get_map_options(self):
        return self.source, self.layers, self.interactive_layer_ids, self.legend

    def __str__(self):
        return self.name
