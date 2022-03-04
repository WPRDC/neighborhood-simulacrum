from typing import Optional, TYPE_CHECKING

import pystache
from django.db import models

from indicators.data import GeogCollection
from indicators.utils import ErrorRecord, DataResponse, ErrorLevel

if TYPE_CHECKING:
    from geo.models import AdminRegion

from .common import DataViz, VizVariable


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
        (PLAIN, "The value"),
        (FRACTION, "Approximate, human friendly, fraction: value over denominator."),
        (PERCENT, "The value's percent of denominator"),
        (BOTH, "Percent and Fraction"),
    )
    vars = models.ManyToManyField('Variable', through=BigValueVariable)
    note = models.TextField(blank=True, null=True)
    format = models.TextField(max_length=3, choices=FORMAT_CHOICES, default=PLAIN,
                              help_text="Only use percent for numbers with denominators. "
                                        "Variables with 'percent' as a unit should use 'Plain'")

    @property
    def view_width(self):
        return self.width_override or self.DEFAULT_WIDTH

    def _get_viz_options(self, geog_collection: GeogCollection) -> Optional[dict]:
        return {
            'format': self.format
        }


class SentenceVariable(VizVariable):
    viz = models.ForeignKey('Sentence', on_delete=models.CASCADE, related_name='sentence_to_variable')
    variable = models.ForeignKey('Variable', on_delete=models.CASCADE, related_name='variable_to_sentence')

    class Meta:
        unique_together = ('viz', 'variable', 'order',)


class Sentence(Alphanumeric):
    vars = models.ManyToManyField('Variable', through=SentenceVariable)
    text = models.TextField(
        help_text='To place a value in your sentence, use {order}. e.g. "There are {1} cats and {2} dogs in town."')

    def get_text_data(self, geog: 'AdminRegion') -> DataResponse:
        data = ''
        error: ErrorRecord
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
                error = ErrorRecord(level=ErrorLevel.OK, message=None)
            except Exception as e:
                error = ErrorRecord(level=ErrorLevel.ERROR, message=str(e))
        else:
            error = ErrorRecord(level=ErrorLevel.EMPTY,
                                message=f'This Sentence is not available for {geog.name}.')

        return DataResponse(data=data, error=error)
