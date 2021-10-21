import json
import os
import re
from typing import List

import requests
from django.conf import settings
from django.core.management.base import BaseCommand

from indicators.models import Domain, Subdomain, Indicator, SubdomainIndicator

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
                        print(' ', ' ', indicator_obj.name, 'created!' if created else 'found!')

                        for data_viz in indicator['dataVizes']:
                            data_viz_data = requests.get('https://api.profiles.wprdc.org/data-viz/' + data_viz['slug'])
