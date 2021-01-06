import indicators.models


def get_population(geog) -> int:
    pop_var = indicators.models.CensusVariable.objects.get(slug='total-population')
    most_recent_time = indicators.models.TimeAxis.objects.get(slug='most-recent-acs-year').time_parts[0]
    try:
        return pop_var.get_primary_value(geog, most_recent_time)
    except:
        return -1

def get_kid_population(geog) -> int:
    pop_var = indicators.models.CensusVariable.objects.get(slug='population-under-18')
    most_recent_time = indicators.models.TimeAxis.objects.get(slug='most-recent-acs-year').time_parts[0]
    try:
        return pop_var.get_primary_value(geog, most_recent_time)
    except:
        return -1
