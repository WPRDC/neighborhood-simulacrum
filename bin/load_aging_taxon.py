from django.utils.text import slugify

from indicators.models import Taxonomy, Domain, Subdomain, TaxonomyDomain, DomainSubdomain, Topic, SubdomainTopic, \
    Indicator, TopicIndicator, CKANVariable, CKANSource, IndicatorVariable, TimeAxis, CKANRegionalSource

TIME_AXIS = TimeAxis.objects.get(slug='most-recent-acs-year')
CKAN_SOURCE = CKANSource.objects.get(slug='age-friendly-community-index')

with open('/Users/steve/projects/profiles/init/aging.json') as f:
    import json

    data = json.load(f)

# Create taxonomy
txn = Taxonomy.objects.get(slug='state-of-aging')

for domain in data['domains']:
    d_name = domain['name']
    d_slug = f"soa-{slugify(domain['name'])}"
    # create domain and link it to the taxonomy
    d = Domain.objects.create(name=d_name, slug=d_slug)
    td = TaxonomyDomain.objects.create(taxonomy=txn, domain=d, order=0)

    for subdomain in domain['subdomains']:
        sd_name = subdomain['name']
        sd_slug = f"soa-{slugify(subdomain['name'])}"
        t_name = f"AFC {sd_name} Index"
        t_slug = f"soa-{slugify(subdomain['name'])}-index"
        i_name = t_name
        i_slug = t_slug
        v_name = t_name
        v_slug = t_slug

        # create subdomain and link it to taxonomy
        sd = Subdomain.objects.create(name=sd_name, slug=sd_slug)
        dsd = DomainSubdomain.objects.create(domain=d, subdomain=sd, order=0)

        # create a topic and indicator for index score for to subdomain
        topic = Topic.objects.create(name=t_name, slug=t_slug)
        sd_topic = SubdomainTopic.objects.create(subdomain=sd, topic=topic, order=0)

        indicator = Indicator.objects.create(name=i_name, slug=i_slug, time_axis=TIME_AXIS)
        topic_indicator = TopicIndicator.objects.create(topic=topic, indicator=indicator, order=0)

        # create variable for index
        variable = CKANVariable.objects.create(
            name=v_name,
            slug=v_slug,
            aggregation_method='AVG',
            field=subdomain['index_field']
        )
        variable.sources.add(CKAN_SOURCE)
        indicator_variable = IndicatorVariable.objects.create(indicator=indicator, variable=variable, order=0)

