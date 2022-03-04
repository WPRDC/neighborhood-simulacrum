from typing import Optional, TYPE_CHECKING

from django.db import models
from django.db.models import Manager
from rest_framework.exceptions import ValidationError

if TYPE_CHECKING:
    from geo.models import AdminRegion

from .common import DataViz, VizVariable


class Table(DataViz):
    # styles
    DEFAULT = 'default'
    DEMOGRAPHICS = 'demographics'
    STYLE_CHOICES = (
        ('Default', DEFAULT),
        ('Demographics', DEMOGRAPHICS)
    )

    # axes
    GEOGRAPHY = 'geography'
    VARIABLE = 'variable'
    TIME = 'time'
    AXIS_CHOICES = (
        ('Geography', GEOGRAPHY),
        ('Variable', VARIABLE),
        ('Time', TIME)
    )

    vars: Manager['TableVariable'] = models.ManyToManyField('Variable', verbose_name='Rows', through='TableVariable')

    table_style = models.CharField(max_length=40, choices=STYLE_CHOICES)
    show_percent = models.BooleanField(default=True)

    row_axis = models.CharField(max_length=20, choices=AXIS_CHOICES, default=VARIABLE)
    column_axis = models.CharField(max_length=20, choices=AXIS_CHOICES, default=TIME)
    view_axis = models.CharField(max_length=20, choices=AXIS_CHOICES, default=GEOGRAPHY)

    @property
    def view_height(self):
        return (len(self.vars.all()) // 5) + 4

    @property
    def view_width(self):
        return self.width_override or self.DEFAULT_WIDTH

    @property
    def variables(self):
        return self.vars.order_by('variable_to_table')

    def _get_viz_options(self, geog: 'AdminRegion') -> Optional[dict]:
        return {
            'table_style': self.table_style,
            'show_percent': self.show_percent,
            'row_axis': self.row_axis,
            'column_axis': self.column_axis,
            'view_axis': self.view_axis,
        }

    def clean(self):
        """ Ensure that no axis is used twice. """
        if (
                self.row_axis == self.column_axis
                or self.row_axis == self.view_axis
                or self.column_axis == self.view_axis
        ):
            raise ValidationError("Each axis can only be used once.")


class TableVariable(VizVariable):
    viz = models.ForeignKey('Table', on_delete=models.CASCADE, related_name='table_to_variable')
    variable = models.ForeignKey('Variable', on_delete=models.CASCADE, related_name='variable_to_table')

    class Meta:
        unique_together = ('viz', 'variable', 'order',)
