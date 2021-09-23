from django.db import models

from profiles.abstract_models import Described
from .source import Source, CensusSource, CKANSource, CKANGeomSource, CKANRegionalSource
from .time import TimeAxis, RelativeTimeAxis, StaticTimeAxis, StaticConsecutiveTimeAxis
from .variable import Variable, CensusVariable, CKANVariable, CensusVariableSource
from .viz import DataViz, Table, Chart, MiniMap, VizVariable


class Domain(Described):
    """ Main categories for organizing indicators """
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.name


class Subdomain(Described):
    domain = models.ForeignKey('Domain', related_name='subdomains', on_delete=models.PROTECT)
    indicators = models.ManyToManyField('Indicator', related_name='groups', blank=True)

    def __str__(self):
        return self.name


class Indicator(Described):
    LAYOUT_CHOICES = (
        ('A', 'Style A'),
        ('B', 'Style B'),
        ('C', 'Style C'),
        ('D', 'Style D'),
    )

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

    layout = models.CharField(max_length=3, choices=LAYOUT_CHOICES, default='A')

    def __str__(self):
        return f'{self.name} ({self.id})'

    @property
    def hierarchies(self):
        """ Collect possible hierarchies. """
        result = []
        for subdomain in Subdomain.objects.filter(indicators=self):
            result.append({'domain': subdomain.domain, 'subdomain': subdomain})
        return result


class Value(models.Model):
    geog = models.ForeignKey('geo.Geography', on_delete=models.CASCADE, db_index=True)
    variable = models.ForeignKey('Variable', on_delete=models.CASCADE, db_index=True)
    value = models.FloatField(null=True, blank=True)
    margin = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f'{self.variable}/{self.geog} ({self.value}, {self.margin})'
