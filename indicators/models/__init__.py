from django.db import models

from profiles.abstract_models import Described
from .source import Source, CensusSource, CKANSource, CKANGeomSource, CKANRegionalSource
from .time import TimeAxis, RelativeTimeAxis, StaticTimeAxis, StaticConsecutiveTimeAxis
from .variable import Variable, CensusVariable, CKANVariable, CensusVariableSource
from .viz import DataViz, Table, Chart, MiniMap, VizVariable


class SubdomainIndicator(models.Model):
    subdomain = models.ForeignKey('Subdomain', on_delete=models.CASCADE, related_name='subdomain_to_indicator')
    indicator = models.ForeignKey('Indicator', on_delete=models.CASCADE, related_name='indicator_to_subdomain')

    order = models.IntegerField(default=0)

    class Meta:
        unique_together = ('subdomain', 'indicator',)
        ordering = ('order',)

    def __str__(self):
        return f'{self.subdomain.__str__()} ➡ {self.indicator.__str__()}'


class Domain(Described):
    """ Main categories for organizing indicators """
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ('order',)

    def __str__(self):
        return self.name


class Subdomain(Described):
    domain = models.ForeignKey('Domain', related_name='subdomains', on_delete=models.CASCADE)
    order = models.IntegerField(default=0)
    inds = models.ManyToManyField('Indicator', related_name='subdomains', through='SubdomainIndicator')

    @property
    def indicators(self):
        return self.inds.order_by('indicator_to_subdomain')

    class Meta:
        ordering = ('order',)

    def __str__(self):
        return self.name


class IndicatorDataViz(models.Model):
    indicator = models.ForeignKey('Indicator', related_name='indicator_to_dataviz', on_delete=models.CASCADE)
    data_viz = models.ForeignKey('DataViz', related_name='dataviz_to_indicator', on_delete=models.CASCADE)

    order = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.indicator.__str__()} ➡ {self.data_viz.__str__()}'

    class Meta:
        ordering = ('order',)
        unique_together = ('indicator', 'data_viz',)


class Indicator(Described):
    LAYOUT_CHOICES = (
        ('A', 'Style A'),
        ('B', 'Style B'),
        ('C', 'Style C'),
        ('D', 'Style D'),
    )

    """ Indicators """
    long_description = models.TextField(
        help_text='🛑 Deprecated!!! This field will go away soon. Used "Full Description" instead.',
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

    vizes = models.ManyToManyField('DataViz', related_name='new_indicator', through='IndicatorDataViz')

    @property
    def data_vizes(self):
        return self.vizes.order_by('dataviz_to_indicator')

    def __str__(self):
        return f'{self.name}'

    @property
    def hierarchies(self):
        """ Collect possible hierarchies. """
        result = []
        for subdomainThrough in SubdomainIndicator.objects.filter(indicator=self):
            subdomain = subdomainThrough.subdomain
            result.append({'domain': subdomain.domain, 'subdomain': subdomain})
        return result


class Value(models.Model):
    geog = models.ForeignKey('geo.AdminRegion', on_delete=models.CASCADE, db_index=True)
    variable = models.ForeignKey('Variable', on_delete=models.CASCADE, db_index=True)
    value = models.FloatField(null=True, blank=True)
    margin = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f'{self.variable}/{self.geog} ({self.value}, {self.margin})'
