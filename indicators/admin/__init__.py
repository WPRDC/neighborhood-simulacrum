from django.contrib import admin
from .indicator import IndicatorAdmin
from .source import CensusSourceAdmin, CKANSourceAdmin, CKANRegionalSourceAdmin, CKANGeomSourceAdmin
from .time import StaticTimeAxisAdmin, StaticConsecutiveTimeAxisAdmin, RelativeTimeAxisAdmin
from .variable import VariableAdmin, CensusVariableAdmin, CKANVariableAdmin
from ..models import Topic, Subdomain, Domain, Value, SubdomainTopic, TopicIndicator, Taxonomy, TaxonomyDomain


class SubdomainTopicInline(admin.StackedInline):
    model = SubdomainTopic


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


@admin.register(Subdomain)
class SubdomainAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)
    prepopulated_fields = {"slug": ("name",)}
    inlines = (SubdomainTopicInline,)


class SubdomainInline(admin.TabularInline):
    model = Subdomain


@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)
    prepopulated_fields = {"slug": ("name",)}

    inlines = (SubdomainInline,)


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
