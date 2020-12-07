from typing import List

from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from polymorphic.models import PolymorphicModel

from geo.models import CensusGeography
from indicators.helpers import clean_sql
from indicators.models.abstract import Described


class DataViz(PolymorphicModel, Described):
    time_axis = models.ForeignKey('TimeAxis', related_name='data_vizes', on_delete=models.CASCADE)
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
    paint = models.JSONField(null=True, blank=True)
    layout = models.JSONField(null=True, blank=True)
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
                | t1  | t2
        cat A   | data      | data
        cat B   | data      | data
    """
    transpose = models.BooleanField(default=False)
    show_percent = models.BooleanField(default=True)

    @property
    def variables(self):
        return self.vars.order_by('variable_to_viz')

    def get_table_data(self, region: CensusGeography) -> List[dict]:
        data = []
        for variable in self.variables.order_by('variable_to_viz'):
            data.append(variable.get_table_row(self, region))
        return data


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

    def get_chart_data(self, region: CensusGeography) -> List[dict]:
        data = []
        for variable in self.variables.order_by('variable_to_viz'):
            data.append(variable.get_chart_record(self, region))
        return data

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
        print(var)
        for time_part in instance.time_axis.time_parts:
            if not var.can_handle_time_part(time_part):
                raise ValidationError(f'{var.slug} is not available in time {time_part.slug}')

