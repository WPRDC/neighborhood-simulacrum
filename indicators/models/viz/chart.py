from typing import Optional, TYPE_CHECKING

from django.db import models
from django.db.models import QuerySet, Manager

if TYPE_CHECKING:
    from geo.models import AdminRegion
    from ..variable import Variable

from .common import DataViz, VizVariable


class Chart(DataViz):
    """ Abstract base class for charts """
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
    legend_type = models.CharField(max_length=10, choices=LEGEND_TYPE_CHOICES, default='circle')

    @property
    def options(self) -> dict:
        return {}

    def get_neighbor_geogs(self, geog: 'AdminRegion') -> QuerySet['AdminRegion']:
        if self.across_geogs:
            return geog.__class__.objects.filter(in_extent=True)
        # default behavior for DataViz subclasses
        return super(Chart, self).get_neighbor_geogs(geog)

    def _get_viz_options(self, geog: 'AdminRegion') -> Optional[dict]:
        return {'legend_type': self.legend_type, }

    class Meta:
        abstract = True


# --- Specific Charts ---
class BarChart(Chart):
    """ Describes a bar or column chart """
    vars = models.ManyToManyField('Variable', verbose_name='Rows', through='BarChartPart')
    as_columns = models.BooleanField(
        verbose_name='Prefer column layout',
        help_text='constraints may require apps and sites to override to bar chart when space is limited.',
        default=False)
    across_geogs = models.BooleanField(
        help_text='Check if you want this chart to compare the statistic '
                  'across geographies instead of across time',
        default=False)

    def _get_viz_options(self, geog: 'AdminRegion') -> Optional[dict]:
        return {'legend_type': self.legend_type, 'across_geogs': self.across_geogs}

    @property
    def options(self):
        return {
            'across_geogs': self.across_geogs,
            'as_columns': self.as_columns,
        }

    class BarChartPart(VizVariable):
        """ Links bar chart to variables """
        viz = models.ForeignKey('BarChart', on_delete=models.CASCADE, related_name='bar_chart_to_variable')
        variable = models.ForeignKey('Variable', on_delete=models.CASCADE, related_name='variable_to_bar_chart')

        class Meta:
            unique_together = ('viz', 'variable', 'order',)


class LineChart(Chart):
    """ Describes a line or area chart """
    vars = models.ManyToManyField('Variable', verbose_name='Lines', through='LineChartPart')
    as_area = models.BooleanField(verbose_name='As stacked area chart')

    class LineChartPart(VizVariable):
        """ Links chart to variables """
        viz = models.ForeignKey('LineChart', on_delete=models.CASCADE, related_name='line_chart_to_variable')
        variable = models.ForeignKey('Variable', on_delete=models.CASCADE, related_name='variable_to_line_chart')

        class Meta:
            unique_together = ('viz', 'variable', 'order',)


class PieChart(Chart):
    """ Describes a pie or donut chart """
    vars = models.ManyToManyField('Variable', verbose_name='Sections', through='PieChartPart')
    as_donut = models.BooleanField(verbose_name='As donut chart')

    class PieChartPart(VizVariable):
        """ Links chart to variables """
        viz = models.ForeignKey('PieChart', on_delete=models.CASCADE, related_name='pie_chart_to_variable')
        variable = models.ForeignKey('Variable', on_delete=models.CASCADE, related_name='variable_to_pie_chart')

        class Meta:
            unique_together = ('viz', 'variable', 'order',)


class PyramidChart(Chart):
    """ Describes a pyramid chart """
    left_vars = models.ManyToManyField(
        'Variable',
        verbose_name='Left bars',
        through='PyramidChartLeftPart',
        related_name='left_pyramid_chart'
    )
    right_vars = models.ManyToManyField(
        'Variable',
        verbose_name='Right bars',
        through='PyramidChartRightPart',
        related_name='right_pyramid_chart'

    )

    @property
    def vars(self) -> Manager['Variable']:
        """ Union the two variable axes for the full set of variables. """
        full_set = self.left_vars.all() | self.right_vars.all()
        return full_set.as_manager()

    class PyramidChartLeftPart(VizVariable):
        """ Links chart to variables """
        viz = models.ForeignKey(
            'PyramidChart',
            on_delete=models.CASCADE,
            related_name='left_pyramid_chart_to_variable'
        )
        variable = models.ForeignKey(
            'Variable',
            on_delete=models.CASCADE,
            related_name='variable_to_left_pyramid_chart'
        )

        class Meta:
            unique_together = ('viz', 'variable', 'order',)

    class PyramidChartRightPart(VizVariable):
        """ Links chart to variables """
        viz = models.ForeignKey(
            'PyramidChart',
            on_delete=models.CASCADE,
            related_name='right_pyramid_chart_to_variable'
        )
        variable = models.ForeignKey(
            'Variable',
            on_delete=models.CASCADE,
            related_name='variable_to_right_pyramid_chart'
        )

        class Meta:
            unique_together = ('viz', 'variable', 'order',)


class ScatterPlot(Chart):
    """ Scatter plot across geographies."""
    x_var = models.ForeignKey(
        'Variable', verbose_name='Horizontal axis variable',
        on_delete=models.CASCADE,
        related_name='x_scatter_plot'
    )
    y_var = models.ForeignKey(
        'Variable', verbose_name='Vertical axis variable',
        on_delete=models.CASCADE,
        related_name='y_scatter_plot'
    )

    @property
    def vars(self) -> Manager['Variable']:
        return Variable.objects.filter(id__in=[self.x_var_id, self.y_var_id]).as_manager()


class Histogram(Chart):
    """ Displays a histogram of the distribution of values from the variable across all geogs. """
    var = models.ForeignKey(
        'Variable', verbose_name='Distribution variable',
        on_delete=models.CASCADE
    )
    n_buckets = models.IntegerField(verbose_name='Number of buckets', help_text='0 = auto', default=0)

    @property
    def vars(self) -> Manager['Variable']:
        return Variable.objects.filter(id=self.var)
