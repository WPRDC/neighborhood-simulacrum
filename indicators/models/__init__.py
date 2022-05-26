from typing import List

from django.db import models
from django.db.models import QuerySet

from context.models import WithContext, WithTags
from profiles.abstract_models import Described
from .indicator import Indicator, IndicatorVariable
from .source import Source, CensusSource, CKANSource, CKANGeomSource, CKANRegionalSource
from .time import TimeAxis, RelativeTimeAxis, StaticTimeAxis, StaticConsecutiveTimeAxis
from .variable import Variable, CensusVariable, CKANVariable, CensusVariableSource


class SubdomainTopic(models.Model):
    subdomain = models.ForeignKey('Subdomain', on_delete=models.CASCADE, related_name='subdomain_to_topic')
    topic = models.ForeignKey('Topic', on_delete=models.CASCADE, related_name='topic_to_subdomain')

    order = models.IntegerField(default=0)

    class Meta:
        unique_together = ('subdomain', 'topic',)
        ordering = ('order',)

    def __str__(self):
        return f'{self.subdomain.__str__()} ➡ {self.topic.__str__()}'


class TaxonomyDomain(models.Model):
    taxonomy = models.ForeignKey('Taxonomy', on_delete=models.CASCADE, related_name='taxonomy_to_domain')
    domain = models.ForeignKey('Domain', on_delete=models.CASCADE, related_name='domain_to_taxonomy')

    order = models.IntegerField(default=0)

    class Meta:
        unique_together = ('taxonomy', 'domain',)
        ordering = ('order',)

    def __str__(self):
        return f'{self.taxonomy.__str__()} ➡ {self.domain.__str__()}'


class Taxonomy(Described, WithTags, WithContext):
    _domains = models.ManyToManyField('Domain', related_name='project', through=TaxonomyDomain)

    @property
    def domains(self):
        return self._domains.order_by('domain_to_taxonomy')

    class Meta:
        verbose_name = 'Taxonomy'
        verbose_name_plural = 'Taxonomies'


class Domain(Described, WithTags, WithContext):
    """ Main categories for organizing indicators """

    @property
    def children(self) -> List[QuerySet]:
        return [self.subdomains.all()]


class Subdomain(Described, WithTags, WithContext):
    domain = models.ForeignKey('Domain', related_name='subdomains', on_delete=models.CASCADE)
    order = models.IntegerField(default=0)
    inds = models.ManyToManyField('Topic', related_name='subdomains', through='SubdomainTopic')

    @property
    def topics(self):
        return self.inds.order_by('topic_to_subdomain')

    @property
    def children(self) -> List[QuerySet]:
        return [self.inds.all()]

    @property
    def parents(self) -> List[QuerySet]:
        return [Domain.objects.filter(id=self.domain.id)]

    class Meta:
        ordering = ('order',)


class TopicIndicator(models.Model):
    topic = models.ForeignKey('Topic', related_name='topic_to_indicator', on_delete=models.CASCADE)
    indicator = models.ForeignKey('Indicator', related_name='indicator_to_topic', on_delete=models.CASCADE)

    order = models.IntegerField(default=0)
    primary = models.BooleanField(default=False, help_text='prioritize this indicator for display in the topic card')

    def __str__(self):
        return f'{self.topic.__str__()} ➡ {self.indicator.__str__()}'

    class Meta:
        ordering = ('order',)
        unique_together = ('topic', 'indicator',)


class Topic(Described, WithTags, WithContext):
    LAYOUT_CHOICES = (
        ('A', 'Style A'),
        ('B', 'Style B'),
        ('C', 'Style C'),
        ('D', 'Style D'),
    )
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

    inds = models.ManyToManyField('Indicator', related_name='topic', through='TopicIndicator')

    @property
    def indicators(self) -> QuerySet['Indicator']:
        return self.inds.order_by('Indicator_to_topic')

    @property
    def hierarchies(self):
        """ Collect possible hierarchies. """
        result = []
        for subdomainThrough in SubdomainTopic.objects.filter(topic=self):
            subdomain = subdomainThrough.subdomain
            result.append({'domain': subdomain.domain, 'subdomain': subdomain})
        return result

    @property
    def children(self) -> List[QuerySet]:
        return [self.indicators]

    @property
    def parents(self) -> List[QuerySet]:
        return [self.topic_to_subdomain.all()]


class Value(models.Model):
    geog = models.ForeignKey('geo.AdminRegion', on_delete=models.CASCADE, db_index=True)
    variable = models.ForeignKey('Variable', on_delete=models.CASCADE, db_index=True)
    value = models.FloatField(null=True, blank=True)
    margin = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f'{self.variable}/{self.geog} ({self.value}, {self.margin})'
