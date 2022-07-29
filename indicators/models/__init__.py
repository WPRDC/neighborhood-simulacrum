from functools import lru_cache
from typing import List

from django.db import models
from django.db.models import QuerySet

from context.models import WithContext, WithTags
from profiles.abstract_models import Described
from .indicator import Indicator, IndicatorVariable
from .source import Source, CensusSource, CKANSource, CKANGeomSource, CKANRegionalSource
from .time import TimeAxis, RelativeTimeAxis, StaticTimeAxis, StaticConsecutiveTimeAxis
from .variable import Variable, CensusVariable, CKANVariable, CensusVariableSource


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


class DomainTopic(models.Model):
    domain = models.ForeignKey('Domain', on_delete=models.CASCADE, related_name='domain_to_topic')
    topic = models.ForeignKey('Topic', on_delete=models.CASCADE, related_name='topic_to_domain')

    order = models.IntegerField(default=0)

    class Meta:
        unique_together = ('domain', 'topic',)
        ordering = ('order',)

    def __str__(self):
        return f'{self.domain.__str__()} ➡ {self.topic.__str__()}'


class SubdomainTopic(models.Model):
    subdomain = models.ForeignKey('Subdomain', on_delete=models.CASCADE, related_name='subdomain_to_topic')
    topic = models.ForeignKey('Topic', on_delete=models.CASCADE, related_name='topic_to_subdomain')

    order = models.IntegerField(default=0)

    class Meta:
        unique_together = ('subdomain', 'topic',)
        ordering = ('order',)

    def __str__(self):
        return f'{self.subdomain.__str__()}-{self.topic.__str__()}'


class DomainSubdomain(models.Model):
    domain = models.ForeignKey('Domain', on_delete=models.CASCADE, related_name='domain_to_subdomain')
    subdomain = models.ForeignKey('Subdomain', on_delete=models.CASCADE, related_name='subdomain_to_domain')

    order = models.IntegerField(default=0)

    class Meta:
        unique_together = ('domain', 'subdomain',)
        ordering = ('order',)

    def __str__(self):
        return f'{self.domain.__str__()} ➡ {self.subdomain.__str__()}'


class Subdomain(Described, WithTags, WithContext):
    topics = models.ManyToManyField('Topic', related_name='subdomains', through=SubdomainTopic)


class Domain(Described, WithTags, WithContext):
    """ Main categories for organizing indicators """
    subdomains = models.ManyToManyField('Subdomain', related_name='subdomains', through=DomainSubdomain)
    topics = models.ManyToManyField('Topic', related_name='domains', through=DomainTopic)

    @property
    def children(self) -> List[QuerySet]:
        return [self.topics.all()]

    @property
    def ordered_subdomains(self):
        return self.subdomains.order_by('subdomain_to_domain')


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
        return self.inds.order_by('indicator_to_topic')

    @property
    def hierarchies(self) -> list[list]:
        """ Collect possible hierarchies. """
        results = []
        taxonomy: Taxonomy

        possible_subdomains = Subdomain.objects.filter(
            subdomain_to_topic__in=SubdomainTopic.objects.filter(topic=self)
        )
        possible_domains = Domain.objects.filter(
            domain_to_subdomain__in=DomainSubdomain.objects.filter(subdomain__in=possible_subdomains)
        )

        for taxonomy in Taxonomy.objects.all():
            try:
                domain = taxonomy.domains.filter(id__in=[rcd['id'] for rcd in possible_domains.values('id')])[0]
                subdomain = domain.subdomains.filter(id__in=[rcd['id'] for rcd in possible_subdomains.values('id')])[0]
                results.append([taxonomy, domain, subdomain])
            except IndexError:
                pass

        return results

    @property
    def children(self) -> List[QuerySet]:
        return [self.indicators]

    @property
    def parents(self) -> List[QuerySet]:
        return [self.topic_to_domain.all()]


class Value(models.Model):
    geog = models.ForeignKey('geo.AdminRegion', on_delete=models.CASCADE, db_index=True)
    variable = models.ForeignKey('Variable', on_delete=models.CASCADE, db_index=True)
    value = models.FloatField(null=True, blank=True)
    margin = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f'{self.variable}/{self.geog} ({self.value}, {self.margin})'
