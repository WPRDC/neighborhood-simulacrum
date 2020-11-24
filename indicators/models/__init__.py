from django.db import models

from .series import Series, YearSeries
from .source import Source, CensusSource, CKANSource, CKANGeomSource, CKANRegionalSource
from .variable import Variable, CensusVariable, CKANVariable, CensusValue, CensusVariableSource
from .viz import DataViz, Table, MiniMap, VizVariable

from .abstract import Described


class Domain(Described):
    """ Main categories for organizing indicators """
    subdomains = models.ManyToManyField('Subdomain', related_name='domains', blank=True)

    def __str__(self):
        return self.name


class Subdomain(Described):
    indicators = models.ManyToManyField('Indicator', related_name='groups', blank=True)

    def __str__(self):
        return self.name


class Indicator(Described):
    """ Indicators """
    long_description = models.TextField(
        help_text='A thorough description for long-form representation.',
        blank=True,
        null=True,
    )
    limitations = models.TextField(
        help_text='Describe what limitations the data may have '
                  '(e.g. small sample size, difficulties in collecting data',
        blank=True,
        null=True,
    )
    importance = models.TextField(
        help_text='Describe the data collection process, highlighting areas '
                  'where bias and assumptions made during the collection '
                  'can impact how the data are interpreted',
        blank=True,
        null=True,
    )
    source = models.TextField(
        help_text='Describe the data collection process, highlighting areas '
                  'where bias and assumptions made during the collection '
                  'can impact how the data are interpreted',
        blank=True,
        null=True,
    )
    provenance = models.TextField(
        help_text='Describe the data collection process, highlighting areas '
                  'where bias and assumptions made during the collection '
                  'can impact how the data are interpreted',
        blank=True,
        null=True,
    )

    # available_regions = models.ManyToManyField(
    #     'geo.Geography',
    #     related_name='%(class)s',
    #     blank=True
    # )

    def __str__(self):
        return f'{self.name} ({self.id})'


class Value(models.Model):
    region = models.ForeignKey('geo.Geography', on_delete=models.CASCADE, db_index=True)
    variable = models.ForeignKey('Variable', on_delete=models.CASCADE, db_index=True)
    value = models.FloatField(null=True, blank=True)
    margin = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f'{self.variable}/{self.region} ({self.value}, {self.margin})'
