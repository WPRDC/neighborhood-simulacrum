from django.contrib import admin
from .indicator import IndicatorAdmin
from .source import CensusSourceAdmin, CKANSourceAdmin, CKANRegionalSourceAdmin, CKANGeomSourceAdmin
from .time import StaticTimeAxisAdmin, StaticConsecutiveTimeAxisAdmin, RelativeTimeAxisAdmin
from .variable import VariableAdmin, CensusVariableAdmin, CKANVariableAdmin
from ..models import Topic, Domain, Value, TopicIndicator, Taxonomy, TaxonomyDomain, \
    DomainTopic, Subdomain, DomainSubdomain, SubdomainTopic


class TopicIndicatorInline(admin.StackedInline):
    model = TopicIndicator
    autocomplete_fields = ('indicator',)


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'description',
    )

    inlines = (TopicIndicatorInline,)
    search_fields = ('name',)
    prepopulated_fields = {"slug": ("name",)}


class SubdomainTopicInline(admin.TabularInline):
    model = SubdomainTopic
    autocomplete_fields = ('topic',)


class DomainTopicInline(admin.TabularInline):
    model = DomainTopic


class DomainSubdomainInline(admin.TabularInline):
    model = DomainSubdomain


@admin.register(Subdomain)
class SubdomainAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)
    prepopulated_fields = {"slug": ("name",)}

    inlines = (SubdomainTopicInline,)


@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)
    prepopulated_fields = {"slug": ("name",)}

    inlines = (DomainSubdomainInline, DomainTopicInline,)


class TaxonomyDomainInline(admin.TabularInline):
    model = TaxonomyDomain
    autocomplete_fields = ('domain',)


@admin.register(Taxonomy)
class TaxonomyAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)
    prepopulated_fields = {"slug": ("name",)}

    inlines = (TaxonomyDomainInline,)


@admin.register(Value)
class ValueAdmin(admin.ModelAdmin):
    pass
