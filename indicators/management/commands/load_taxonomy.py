import json
import os
import re
from typing import List, Dict, Type

import requests
from django.conf import settings
from django.core.management.base import BaseCommand

from indicators.models import Domain, Subdomain, Indicator, SubdomainIndicator, TimeAxis, Variable
from indicators.models.viz import DataViz, \
    Table, TableRow, \
    MiniMap, MapLayer, \
    Chart, ChartPart, \
    BigValue, BigValueVariable

MODEL_MAP: Dict[str, Type['DataViz']] = {
    'Table': Table,
    'MiniMap': MiniMap,
    'Chart': Chart,
    'BigValue': BigValue,
}

THROUGH_MODEL_MAP: Dict[str, Type['DataViz']] = {
    'Table': TableRow,
    'MiniMap': MapLayer,
    'Chart': ChartPart,
    'BigValue': BigValueVariable,
}

BASE_FIELDS = ['name', 'slug', 'description']

pattern = re.compile(r'(?<!^)(?=[A-Z])')


def camel_to_snake(name):
    return pattern.sub('_', name).lower()


class Command(BaseCommand):
    help = "Load standard geographies"

    def add_arguments(self, parser):
        # todo: add arguments that map to the `load_census_boundaries.run()` ones
        pass

    def handle(self, *args, **options):
        taxonomy_file = os.path.join(settings.BASE_DIR, 'indicators', 'data', 'taxonomy-20211025.json')
        with open(taxonomy_file) as f:
            taxonomy: List[dict] = json.load(f)
            for domain in taxonomy['results']:
                domain_data = {camel_to_snake(k): v for k, v in domain.items() if k != 'subdomains'}
                domain_obj, created = Domain.objects.get_or_create(**domain_data)
                print(domain_obj.name, 'created!' if created else 'found!')

                for subdomain in domain['subdomains']:
                    subdomain_data = {camel_to_snake(k): v for k, v in subdomain.items() if k != 'indicators'}
                    subdomain_obj, created = Subdomain.objects.get_or_create(**subdomain_data, domain_id=domain_obj.id)
                    print(' ', subdomain_obj.name, 'created!' if created else 'found!')
                    i = 0
                    for indicator in subdomain['indicators']:
                        indicator_data = {camel_to_snake(k): v for k, v in indicator.items() if
                                          k not in ('dataVizes', 'hierarchies',)}
                        indicator_obj, created = Indicator.objects.get_or_create(**indicator_data)
                        SubdomainIndicator.objects.get_or_create(
                            subdomain=subdomain_obj,
                            indicator=indicator_obj,
                            order=i
                        )
                        i += 1
                        print('  ', indicator_obj.name, 'created!' if created else 'found!')

                        for data_viz in indicator['dataVizes']:
                            # get the detailed data for the viz
                            data_viz_slug = data_viz["slug"]
                            if len(DataViz.objects.filter(slug=data_viz_slug)):
                                print('   ', data_viz_slug, 'found! Skipping...')
                                continue

                            r = requests.get(f'https://api.profiles.wprdc.org/data-viz/{data_viz_slug}/')
                            viz_data = r.json()
                            viz_type = viz_data['vizType']

                            # start building up the viz
                            viz_model = MODEL_MAP[viz_type]
                            base_fields = {field: viz_data[field] for field in BASE_FIELDS}
                            viz = viz_model(**base_fields)
                            viz.time_axis = TimeAxis.objects.get(slug=viz_data['timeAxis']['slug'])
                            viz.indicator = indicator_obj
                            viz.save()
                            print('   ', viz.name, 'created!')
                            # create through model objects that connect vizes to variables
                            v_no = 0
                            for variable in viz_data['variables']:
                                var = Variable.objects.get(slug=variable['slug'])
                                through_model = THROUGH_MODEL_MAP[viz_type]
                                tmodel, created = through_model.objects.get_or_create(viz=viz, variable=var, order=v_no)
                                v_no += 1
                                print('    ', tmodel, 'created!' if created else 'found!')
