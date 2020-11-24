from indicators.models import CensusVariable, Indicator, Value
from geo.models import BlockGroup, Tract, County, CountySubdivision
from indicators.utils import get_census_variable_at_region, get_indicator_at_region

bg = BlockGroup.objects.all()[1]
tract = Tract.objects.all()[1]
county = County.objects.all()[1]
countysub = CountySubdivision.objects.all()[1]

regions = [bg, tract, county, countysub]


def run():
    for value in Value.objects.all():
        value.delete()

    for indicator in Indicator.objects.all():
        for region in regions:
            get_indicator_at_region(indicator, region)
