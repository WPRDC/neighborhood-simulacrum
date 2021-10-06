from django.contrib import admin
from django.contrib.gis.admin import GeoModelAdmin
from .models import AdminRegion, BlockGroup, Tract, \
    CountySubdivision, SchoolDistrict, County, Neighborhood, \
    ZipCodeTabulationArea


@admin.register(AdminRegion)
class AdminRegionAdmin(GeoModelAdmin):
    list_display = (
        'id',
        'name',
        'common_geoid',
        'geog_path',
    )
    search_fields = ('name',)


# CENSUS GEOGRAPHIES
@admin.register(BlockGroup)
class BlockGroupAdmin(GeoModelAdmin):
    list_display = (
        'id',
        'name',
        'common_geoid',
        'geoid',
        'affgeoid',
        'statefp',
        'countyfp',
        'tractce',
    )
    list_filter = ('statefp', 'countyfp')
    search_fields = ('name',)


@admin.register(Tract)
class TractAdmin(GeoModelAdmin):
    list_display = (
        'id',
        'name',
        'common_geoid',
        'geoid',
        'affgeoid',
        'statefp',
        'countyfp',
    )
    list_filter = ('statefp', 'countyfp')
    search_fields = ('name',)


@admin.register(ZipCodeTabulationArea)
class ZipCodeTabulationAreaAdmin(GeoModelAdmin):
    list_display = (
        'id',
        'name',
        'common_geoid',
        'geoid',
        'affgeoid',
    )
    search_fields = ('name',)


@admin.register(CountySubdivision)
class CountySubdivisionAdmin(GeoModelAdmin):
    list_display = (
        'id',
        'name',
        'common_geoid',
        'geoid',
        'affgeoid',
        'statefp',
        'countyfp',
        'cousubfp',
        'cousubns',
    )
    list_filter = ('statefp', 'countyfp')
    search_fields = ('name',)


@admin.register(SchoolDistrict)
class SchoolDistrictAdmin(GeoModelAdmin):
    list_display = (
        'id',
        'name',
        'common_geoid',
        'geoid',
        'affgeoid',
        'statefp',
        'unsdlea',
        'placens',
    )
    search_fields = ('name',)


@admin.register(County)
class CountyAdmin(GeoModelAdmin):
    list_display = (
        'id',
        'name',
        'common_geoid',
        'geoid',
        'affgeoid',
        'statefp',
    )
    list_filter = ('statefp', 'countyfp')
    search_fields = ('name',)


# END CENSUS GEOGRAPHIES

@admin.register(Neighborhood)
class NeighborhoodAdmin(GeoModelAdmin):
    list_display = (
        'id',
        'name',
        'common_geoid'
    )
    search_fields = ('name',)
