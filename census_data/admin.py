from django.contrib import admin

from census_data.models import CensusTableRecord

@admin.register(CensusTableRecord)
class CensusTableRecordAdmin(admin.ModelAdmin):
    list_display = ('table_id', 'dataset', 'year')
    search_fields = ('table_id', 'dataset')
