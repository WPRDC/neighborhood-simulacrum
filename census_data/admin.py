from django.contrib import admin

# Register your models here.
from census_data.models import CensusTable, CensusTablePointer


@admin.register(CensusTable)
class CensusTableAdmin(admin.ModelAdmin):
    list_display = ('table_id', 'description')
    search_fields = ('description', 'table_id')


@admin.register(CensusTablePointer)
class CensusTablePointerAdmin(admin.ModelAdmin):
    list_display = ('table_id', 'dataset')
    search_fields = ('table_id', 'dataset')
