import os

from django.conf import settings
from django.contrib.gis.utils import LayerMapping

from geo import models

DATA_DIR = os.path.join(settings.BASE_DIR, 'data', 'geo', '2019')

mappings = {
    'block_group': {
        'model': models.BlockGroup,
        'level': models.CensusGeography.BLOCK_GROUP,
        'file_name': 'cb_2019_42_bg_500k',
        'mapping': {
            'name': 'NAME',
            'geom': 'MULTIPOLYGON',
            'geoid': 'GEOID',
            'global_geoid': 'GEOID',
            'statefp': 'STATEFP',
            'countyfp': 'COUNTYFP',
            'tractce': 'TRACTCE',
            'blkgrpce': 'BLKGRPCE',
            'affgeoid': 'AFFGEOID',
            'lsad': 'LSAD',
            'aland': 'ALAND',
            'awater': 'AWATER',
        }
    },
    'tract': {
        'model': models.Tract,
        'level': models.CensusGeography.TRACT,
        'file_name': 'cb_2019_42_tract_500k',
        'mapping': {
            'name': 'NAME',
            'geom': 'MULTIPOLYGON',
            'geoid': 'GEOID',
            'global_geoid': 'GEOID',
            'statefp': 'STATEFP',
            'countyfp': 'COUNTYFP',
            'tractce': 'TRACTCE',
            'affgeoid': 'AFFGEOID',
            'aland': 'ALAND',
            'awater': 'AWATER',
        }
    },
    'county_subdivision': {
        'model': models.CountySubdivision,
        'level': models.CensusGeography.COUNTY_SUBDIVISION,
        'file_name': 'cb_2019_42_cousub_500k',
        'mapping': {
            'name': 'NAME',
            'geom': 'MULTIPOLYGON',
            'geoid': 'GEOID',
            'global_geoid': 'GEOID',
            'statefp': 'STATEFP',
            'countyfp': 'COUNTYFP',
            'cousubfp': 'COUSUBFP',
            'cousubns': 'COUSUBNS',
            'affgeoid': 'AFFGEOID',
            'aland': 'ALAND',
            'awater': 'AWATER',
        }
    },
    'place': {
        'model': models.Place,
        'level': models.CensusGeography.PLACE,
        'file_name': 'cb_2019_42_place_500k',
        'mapping': {
            'name': 'NAME',
            'geom': 'MULTIPOLYGON',
            'geoid': 'GEOID',
            'global_geoid': 'GEOID',
            'statefp': 'STATEFP',
            'placefp': 'PLACEFP',
            'placens': 'PLACENS',
            'affgeoid': 'AFFGEOID',
            'aland': 'ALAND',
            'awater': 'AWATER',
        }
    },
    'puma': {
        'model': models.Puma,
        'level': models.CensusGeography.PUMA,
        'file_name': 'cb_2019_42_puma10_500k',
        'mapping': {
            'name': 'NAME10',
            'geom': 'MULTIPOLYGON',
            'geoid': 'GEOID10',
            'statefp': 'STATEFP10',
            'pumace': 'PUMACE10',
            'affgeoid': 'AFFGEOID10',
            'aland': 'ALAND10',
            'awater': 'AWATER10',
        }
    },
    'school_district': {
        'model': models.SchoolDistrict,
        'level': models.CensusGeography.SCHOOL_DISTRICT,
        'file_name': 'cb_2019_42_unsd_500k',
        'mapping': {
            'name': 'NAME',
            'geom': 'MULTIPOLYGON',
            'geoid': 'GEOID',
            'global_geoid': 'GEOID',
            'statefp': 'STATEFP',
            'unsdlea': 'UNSDLEA',
            'affgeoid': 'AFFGEOID',
            'aland': 'ALAND',
            'awater': 'AWATER',
        }
    },
    'state_house': {
        'model': models.StateHouse,
        'level': models.CensusGeography.STATE_HOUSE,
        'file_name': 'cb_2019_42_sldl_500k',
        'mapping': {
            'name': 'NAME',
            'geom': 'MULTIPOLYGON',
            'geoid': 'GEOID',
            'global_geoid': 'GEOID',
            'statefp': 'STATEFP',
            'sldlst': 'SLDLST',
            'affgeoid': 'AFFGEOID',
            'aland': 'ALAND',
            'awater': 'AWATER',
        }
    },
    'state_senate': {
        'model': models.StateSenate,
        'level': models.CensusGeography.STATE_SENATE,
        'file_name': 'cb_2019_42_sldu_500k',
        'mapping': {
            'name': 'NAME',
            'geom': 'MULTIPOLYGON',
            'geoid': 'GEOID',
            'global_geoid': 'GEOID',
            'statefp': 'STATEFP',
            'sldust': 'SLDUST',
            'affgeoid': 'AFFGEOID',
            'aland': 'ALAND',
            'awater': 'AWATER',
        }
    },
    'county': {
        'model': models.County,
        'level': models.CensusGeography.COUNTY,
        'file_name': 'cb_2019_us_county_500k',
        'mapping': {
            'name': 'NAME',
            'geom': 'MULTIPOLYGON',
            'geoid': 'GEOID',
            'global_geoid': 'GEOID',
            'statefp': 'STATEFP',
            'countyfp': 'COUNTYFP',
            'countyns': 'COUNTYNS',
            'affgeoid': 'AFFGEOID',
            'lsad': 'LSAD',
            'aland': 'ALAND',
            'awater': 'AWATER',
        }
    },
    'zcta': {
        'model': models.ZipCodeTabulationArea,
        'level': models.CensusGeography.ZCTA,
        'file_name': 'cb_2018_us_zcta510_500k',
        'mapping': {
            'name': 'ZCTA5CE10',
            'geom': 'MULTIPOLYGON',
            'geoid': 'GEOID10',
            'global_geoid': 'GEOID10',
            'affgeoid': 'AFFGEOID10',
            'aland': 'ALAND10',
            'awater': 'AWATER10',
        }
    },
    'pgh_neighborhoods': {
        'model': models.Neighborhood,
        'level': models.CensusGeography.NEIGHBORHOOD,
        'file_name': 'pgh_neighborhoods',
        'mapping': {
            'name': 'hood',
            'geom': 'MULTIPOLYGON',
            'geoid': 'geoid10',
            'global_geoid': 'geoid10',
            'affgeoid': 'geoid10',
            'aland': 'aland10',
            'awater': 'awater10',
        }
    },
}


def run(ignore=(), only=None, clear_first=False):
    for name, mapping in mappings.items():
        print(name)
        if name in ignore:
            print("--ignored")
            continue

        if only and name not in only:
            print("--skipped")
            continue

        if clear_first:
            print('...truncating table')
        lm = LayerMapping(
            mapping['model'],
            os.path.join(DATA_DIR, name, mapping['file_name'] + '.shp'),
            mapping['mapping']
        )
        try:
            l = lm.save(verbose=True, strict=True)
        except Exception as e:
            print(e)