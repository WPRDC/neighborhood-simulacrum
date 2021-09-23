from django.contrib.gis.db import models
from public_housing import housing_datasets

class ProjectIndex(models.Model):
    id = models.IntegerField(unique=True, primary_key=True)
    full_text = models.TextField(db_column='_full_text', blank=True, null=True)  # Field renamed because it started with '_'. This field type is a guess.
    property_id = models.TextField(blank=True, null=True)
    hud_property_name = models.TextField(blank=True, null=True)
    property_street_address = models.TextField(blank=True, null=True)
    municipality_name = models.TextField(blank=True, null=True)
    city = models.TextField(blank=True, null=True)
    zip_code = models.TextField(blank=True, null=True)
    units = models.TextField(blank=True, null=True)
    scattered_sites = models.CharField(max_length=20, blank=True, null=True)
    latitude = models.TextField(blank=True, null=True)
    longitude = models.TextField(blank=True, null=True)
    census_tract = models.TextField(blank=True, null=True)
    crowdsourced_id = models.TextField(blank=True, null=True)
    house_cat_id = models.TextField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)
    geom = models.PointField(db_column='_geom', blank=True, null=True)  # Field renamed because it started with '_'.
    geom_webmercator = models.PointField(db_column='_the_geom_webmercator', srid=3857, blank=True, null=True)  # Field renamed because it started with '_'.
