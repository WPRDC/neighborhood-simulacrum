GEOG_SOURCE_MAPPINGS = {
    'BlockGroup': {
        'file_name': 'block_group/cb_2019_42_bg_500k.shp',
        'mapping': {
            'name': 'NAME',
            'geom': 'MULTIPOLYGON',
            'geoid': 'GEOID',
            'common_geoid': 'GEOID',
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
    'Tract': {
        'file_name': 'tract/cb_2019_42_tract_500k.shp',
        'mapping': {
            'name': 'NAME',
            'geom': 'MULTIPOLYGON',
            'geoid': 'GEOID',
            'common_geoid': 'GEOID',
            'statefp': 'STATEFP',
            'countyfp': 'COUNTYFP',
            'tractce': 'TRACTCE',
            'affgeoid': 'AFFGEOID',
            'aland': 'ALAND',
            'awater': 'AWATER',
        }
    },
    'CountySubdivision': {
        'file_name': 'county_subdivision/cb_2019_42_cousub_500k.shp',
        'mapping': {
            'name': 'NAME',
            'geom': 'MULTIPOLYGON',
            'geoid': 'GEOID',
            'common_geoid': 'GEOID',
            'statefp': 'STATEFP',
            'countyfp': 'COUNTYFP',
            'cousubfp': 'COUSUBFP',
            'cousubns': 'COUSUBNS',
            'affgeoid': 'AFFGEOID',
            'aland': 'ALAND',
            'awater': 'AWATER',
        }
    },
    'SchoolDistrict': {
        'file_name': 'school_district/cb_2019_42_unsd_500k.shp',
        'mapping': {
            'name': 'NAME',
            'geom': 'MULTIPOLYGON',
            'geoid': 'GEOID',
            'common_geoid': 'GEOID',
            'statefp': 'STATEFP',
            'unsdlea': 'UNSDLEA',
            'affgeoid': 'AFFGEOID',
            'aland': 'ALAND',
            'awater': 'AWATER',
        }
    },
    'County': {
        'file_name': 'county/cb_2019_us_county_500k.shp',
        'mapping': {
            'name': 'NAME',
            'geom': 'MULTIPOLYGON',
            'geoid': 'GEOID',
            'common_geoid': 'GEOID',
            'statefp': 'STATEFP',
            'countyfp': 'COUNTYFP',
            'countyns': 'COUNTYNS',
            'affgeoid': 'AFFGEOID',
            'lsad': 'LSAD',
            'aland': 'ALAND',
            'awater': 'AWATER',
        }
    },
    'ZipCodeTabulationArea': {
        'file_name': 'zcta/cb_2018_us_zcta510_500k.shp',
        'mapping': {
            'name': 'ZCTA5CE10',
            'geom': 'MULTIPOLYGON',
            'geoid': 'GEOID10',
            'common_geoid': 'GEOID10',
            'affgeoid': 'AFFGEOID10',
            'aland': 'ALAND10',
            'awater': 'AWATER10',
        }
    },
    'Neighborhood': {
        'file_name': 'pgh_neighborhoods/pgh_neighborhoods.shp',
        'mapping': {
            'name': 'hood',
            'geom': 'MULTIPOLYGON',
            'common_geoid': 'geoid10',
        }
    },
}