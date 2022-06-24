from django.contrib import admin
from .indicator import IndicatorAdmin
from .source import CensusSourceAdmin, CKANSourceAdmin, CKANRegionalSourceAdmin, CKANGeomSourceAdmin
from .time import StaticTimeAxisAdmin, StaticConsecutiveTimeAxisAdmin, RelativeTimeAxisAdmin
from .variable import VariableAdmin, CensusVariableAdmin, CKANVariableAdmin
from ..models import Topic, Domain, Value, TopicIndicator, Taxonomy, TaxonomyDomain, \
    DomainTopic



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


class DomainTopicInline(admin.TabularInline):
    model = DomainTopic


@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)
    prepopulated_fields = {"slug": ("name",)}

    inlines = (DomainTopicInline,)


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
