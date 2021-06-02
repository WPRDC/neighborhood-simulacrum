from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from geo.models import BlockGroup, Tract, CountySubdivision, County, Neighborhood, ZipCodeTabulationArea, SchoolDistrict, StateSenate, StateHouse, Place, Puma
from indicators.utils import limit_to_geo_extent


class Command(BaseCommand):
    help = "Load standard geographies"

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        for model in (Neighborhood,):
            new_ct = ContentType.objects.get_for_model(model)
            print(model, new_ct)
            print(model.objects.all().update(polymorphic_ctype=new_ct))
