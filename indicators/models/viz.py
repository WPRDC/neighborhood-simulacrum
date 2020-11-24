from typing import List

from django.db import models
from django.contrib.postgres.fields import ArrayField, JSONField
from polymorphic.models import PolymorphicModel

from geo.models import CensusGeography
from indicators.helpers import clean_sql
from indicators.models.abstract import Described


class DataViz(Described, PolymorphicModel):
    series = models.ManyToManyField('Series', related_name='data_vizes')
    vars = models.ManyToManyField('Variable', through='VizVariable')
    indicator = models.ForeignKey('Indicator', related_name='data_vizes', on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Data Visualization"
        verbose_name_plural = "Data Visualizations"

    @property
    def variables(self):
        return self.vars.order_by('variable_to_viz')


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
    paint = JSONField(null=True, blank=True)
    layout = JSONField(null=True, blank=True)
    filter = models.TextField(null=True, blank=True)

    @property
    def unfiltered_sql(self):
        return f"SELECT {self.fields.join(', ')} FROM {self.carto_table}"

    def get_sql_for_region(self, region: CensusGeography) -> str:
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
                | series A  | series B
        cat A   | data      | data
        cat B   | data      | data
    """
    transpose = models.BooleanField(default=False)
    show_percent = models.BooleanField(default=True)
    pass

    @property
    def variables(self):
        return self.vars.order_by('variable_to_viz')

    def get_table_data(self, region: CensusGeography) -> List[dict]:
        data = []
        for variable in self.variables.order_by('variable_to_viz'):
            data.append(variable.get_table_row(self, region))
        return data
