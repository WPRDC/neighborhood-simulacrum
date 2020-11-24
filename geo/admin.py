from django.contrib import admin
from django.contrib.gis.admin import GeoModelAdmin
from .models import Geography, CensusGeography, BlockGroup, Tract, \
    CountySubdivision, Place, Puma, SchoolDistrict, StateHouse, StateSenate, \
    County


@admin.register(Geography)
class GeographyAdmin(GeoModelAdmin):
    list_display = ('id', 'name', 'description',)
    search_fields = ('name',)

    class Meta:
        abstract = True


@admin.register(CensusGeography)
class CensusGeographyAdmin(GeoModelAdmin):
    list_display = (
        'id',
        'name',
        'description',
        'affgeoid',
        'lsad',
        'aland',
        'awater',
    )
    search_fields = ('name',)


@admin.register(BlockGroup)
class BlockGroupAdmin(GeoModelAdmin):
    list_display = (
        'id',
        'name',
        'description',
        'geoid',
        'affgeoid',
        'lsad',
        'aland',
        'awater',
        'statefp',
        'countyfp',
        'tractce',
        'blkgrpce',
    )
    list_filter = ('statefp', 'countyfp')
    search_fields = ('name',)


@admin.register(Tract)
class TractAdmin(GeoModelAdmin):
    list_display = (
        'id',
        'name',
        'description',
        'geoid',
        'affgeoid',
        'lsad',
        'aland',
        'awater',
        'statefp',
        'countyfp',
        'tractce',
    )
    list_filter = ('statefp', 'countyfp')
    search_fields = ('name',)


@admin.register(CountySubdivision)
class CountySubdivisionAdmin(GeoModelAdmin):
    list_display = (
        'id',
        'name',
        'description',
        'geoid',
        'affgeoid',
        'lsad',
        'aland',
        'awater',
        'statefp',
        'countyfp',
        'cousubfp',
        'cousubns',
    )
    list_filter = ('statefp', 'countyfp')
    search_fields = ('name',)


@admin.register(Place)
class PlaceAdmin(GeoModelAdmin):
    list_display = (
        'id',
        'name',
        'description',
        'geoid',
        'affgeoid',
        'lsad',
        'aland',
        'awater',
        'statefp',
        'placefp',
        'placens',
    )
    search_fields = ('name',)


@admin.register(Puma)
class PumaAdmin(GeoModelAdmin):
    list_display = (
        'id',
        'name',
        'description',
        'geoid',
        'affgeoid',
        'lsad',
        'aland',
        'awater',
        'statefp',
        'pumace',
    )
    search_fields = ('name',)


@admin.register(SchoolDistrict)
class SchoolDistrictAdmin(GeoModelAdmin):
    list_display = (
        'id',
        'name',
        'description',
        'geom',
        'affgeoid',
        'lsad',
        'aland',
        'awater',
        'statefp',
        'unsdlea',
        'placens',
    )
    search_fields = ('name',)


@admin.register(StateHouse)
class StateHouseAdmin(GeoModelAdmin):
    list_display = (
        'id',
        'name',
        'description',
        'geoid',
        'affgeoid',
        'lsad',
        'aland',
        'awater',
        'statefp',
        'sldlst',
        'lsy',
    )
    search_fields = ('name',)


@admin.register(StateSenate)
class StateSenateAdmin(GeoModelAdmin):
    list_display = (
        'id',
        'name',
        'description',
        'geoid',
        'affgeoid',
        'lsad',
        'aland',
        'awater',
        'statefp',
        'sldust',
        'lsy',
    )
    search_fields = ('name',)


@admin.register(County)
class CountyAdmin(GeoModelAdmin):
    list_display = (
        'id',
        'name',
        'description',
        'geoid',
        'affgeoid',
        'lsad',
        'aland',
        'awater',
        'statefp',
        'countyfp',
        'countyns',
    )
    list_filter = ('statefp', 'countyfp')
    search_fields = ('name',)
