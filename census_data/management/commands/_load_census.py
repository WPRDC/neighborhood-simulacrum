import asyncio
import csv
import os
import zipfile
from ftplib import FTP
from functools import lru_cache

import pandas as pd
import requests
from asgiref.sync import sync_to_async
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from openpyxl import load_workbook

from census_data.models import CensusTable, CensusValue
from geo.models import AdminRegion

COUNTIES = ('42073', '42003', '42007', '42125', '42059', '42051', '42129', '42063', '42005', '42019',)

DEFAULT_SEQUENCE_NUMBERS = ('3',)

STATE = 'Pennsylvania'  # in PascalCase, e.g. New Mexico is NewMexico
ST = 'pa'  # state abbreviation in lowercase
ACS_YEAR = '2019'

FIVE_YEAR_DIRNAME = '5_year_seq_by_state'
TRACT_DIRNAME = 'Tracts_Block_Groups_Only'
OTHER_GEO_DIRNAME = 'All_Geographies_Not_Tracts_Block_Groups'
TEMPLATE_FILENAME = '2019_5yr_Summary_FileTemplates.zip'
GEO_LOOKUP_FILENAME = 'g20195pa.csv'

FTP_HOST = 'ftp2.census.gov'

# Data location on census ftp
FTP_DIRECTORY = f'/programs-surveys/acs/summary_file/{ACS_YEAR}/data/'
TRACT_BG_DATA_DIR = os.path.join(FTP_DIRECTORY, FIVE_YEAR_DIRNAME, STATE, TRACT_DIRNAME)
OTHER_GEO_DATA_DIR = os.path.join(FTP_DIRECTORY, FIVE_YEAR_DIRNAME, STATE, OTHER_GEO_DIRNAME)
TEMPLATE_PATH = os.path.join(FTP_DIRECTORY, TEMPLATE_FILENAME)
GEO_LOOKUP_PATH = os.path.join(TEMPLATE_PATH, GEO_LOOKUP_FILENAME)

# Where the temp files are downloaded
DATA_DL_DIRECTORY = os.path.join(settings.BASE_DIR, 'data', f'acs5_{ACS_YEAR}')
TRACT_BG_DL_DIR = os.path.join(DATA_DL_DIRECTORY, FIVE_YEAR_DIRNAME, TRACT_DIRNAME)
OTHER_GEO_DL_DIR = os.path.join(DATA_DL_DIRECTORY, FIVE_YEAR_DIRNAME, OTHER_GEO_DIRNAME)
TEMPLATE_ZIP_DL_PATH = os.path.join(DATA_DL_DIRECTORY, FIVE_YEAR_DIRNAME, TEMPLATE_FILENAME)
TEMPLATES_DL_DIR = os.path.join(DATA_DL_DIRECTORY, FIVE_YEAR_DIRNAME, 'templates')
GEO_LOOKUP_DL_PATH = os.path.join(TEMPLATES_DL_DIR, GEO_LOOKUP_FILENAME)


@sync_to_async
def extract_variable_data(fname, mode='e'):
    result = []
    wb = load_workbook(filename=fname)

    # col 6 is when the real data starts
    for i in range(6, len(wb[mode][1])):
        table_id = wb[mode][1][i].value + mode.upper()
        desc = wb[mode][2][i].value
        census_table = CensusTable.objects.get_or_create(year=2019, dataset='ACS5', table_id=table_id, description=desc)
        result.append(census_table[0])

    return result


@sync_to_async
def get_geo(logrecno, geo_lookup):
    formatted_affgeoid = ''
    try:
        affgeoid = geo_lookup[int(logrecno)]
        parts = affgeoid.split('US')
        formatted_affgeoid = f'{int(parts[0]):05}00US{parts[1]}'
        return AdminRegion.objects.get(affgeoid=formatted_affgeoid)
    except ObjectDoesNotExist:
        print(formatted_affgeoid)
        return None
    except Exception as e:
        print(e)
        return None


@sync_to_async
def download_data(ftp, redownload, year):
    # the data for geographies is split across two files
    for (data_dir, dl_dir) in [(TRACT_BG_DATA_DIR, TRACT_BG_DL_DIR), (OTHER_GEO_DATA_DIR, OTHER_GEO_DL_DIR)]:
        ftp.cwd(data_dir)
        print('⬇️', f'Downloading data files from {data_dir}...')
        data_files = ftp.nlst()
        for data_file in data_files:
            # skip the other file(s)
            if data_file[-3:] != 'zip':
                continue

            # check year before downloading
            dl_path = os.path.join(dl_dir, data_file)
            if year is not None:
                if year in dl_path or redownload or not (
                        os.path.isfile(os.path.join(dl_dir, f'e{data_file[:-4]}.txt')) and os.path.isfile(os.path.join(dl_dir, f'm{data_file[:-4]}.txt'))):
                    print('⬇️️', 'Downloading', dl_path)
                    with open(dl_path, 'wb') as f:
                        ftp.retrbinary(f'RETR {data_file}', f.write)
                    # extract files
                    with zipfile.ZipFile(dl_path, 'r') as zf:
                        zf.extractall(dl_dir)
                    # delete zip
                    os.remove(dl_path)
                else:
                    print('❎', 'Skipping', dl_path)

            elif year is None:
                if redownload or not (os.path.isfile(os.path.join(dl_dir, f'e{data_file[:-4]}.txt')) and os.path.isfile(
                        os.path.join(dl_dir, f'm{data_file[:-4]}.txt'))):
                    print('⬇️️', 'Downloading', dl_path)
                    with open(dl_path, 'wb') as f:
                        ftp.retrbinary(f'RETR {data_file}', f.write)
                    # extract files
                    with zipfile.ZipFile(dl_path, 'r') as zf:
                        zf.extractall(dl_dir)
                    # delete zip
                    os.remove(dl_path)
                else:
                    print('❎', 'Skipping', dl_path)

    # download template file zip
    with open(TEMPLATE_ZIP_DL_PATH, 'wb') as f:
        ftp.retrbinary(f'RETR {TEMPLATE_PATH}', f.write)

    with zipfile.ZipFile(TEMPLATE_ZIP_DL_PATH, 'r') as zf:
        zf.extractall(TEMPLATES_DL_DIR)


@sync_to_async
def get_or_create(model, data):
    return model.objects.get_or_create(**data)


@sync_to_async
def get(model, data):
    return model.objects.get(**data)


async def census_values_from_row(row, census_tables, seq_no, mode, geo_lookup):
    census_values = []
    logrecno = row[5]
    geography = geo_lookup[str(int(logrecno))]

    # Only use certain geos
    if not geography or not geography.common_geoid:
        print('❌ not found')
        return []
    if geography.geog_type in ['blockGroup', 'puma', 'stateSenate', 'stateHouse']:
        print('⤵️', geography, geography.affgeoid, 'Skipping geography', geography.geog_type)
        return []
    if geography.common_geoid[:5] not in COUNTIES:
        print('⤵️', geography, geography.affgeoid, 'out of range')
        return []

    print('🏙', geography.title, f'({geography.affgeoid})', f'[{seq_no}{mode.upper()}]')

    # for the cells that have data in them
    for i in range(6, len(row)):
        cell = row[i]
        census_table = census_tables[i - 6]
        # Get value
        try:
            value = float(cell)
        except ValueError:
            value = None
        new_cv = {'geography': geography,
                  'census_table': census_table,
                  'value': value,
                  'raw_value': cell}
        census_values.append(new_cv)

    return census_values


@lru_cache
def format_affgeoid(affgeoid):
    parts = affgeoid.split('US')
    return f'{int(parts[0]):05}00US{parts[1]}'


@sync_to_async
def get_geo_lookup():
    r = requests.get(
        'https://www2.census.gov/programs-surveys/acs/summary_file/2019/documentation/geography/5yr_year_geo/pa.xlsx')

    with open('2019pa.xlsx', 'wb') as output:
        output.write(r.content)

    df = pd.read_excel('2019pa.xlsx')
    log_rec_df = pd.DataFrame()
    log_rec_df['logrecno'] = df['Logical Record Number']
    log_rec_df['affgeoid'] = df['Geography ID']

    log_rec_df.to_csv("logrec_to_geoid.csv", index=False)

    print('🌏', 'Generating geo lookup ')
    lookup = {}

    raw_lookup = csv.DictReader(open('logrec_to_geoid.csv'))

    geos = {cg.affgeoid: cg for cg in AdminRegion.objects.all()}

    for row in raw_lookup:
        logrecno = row['logrecno']
        try:
            affgeoid = format_affgeoid(row['affgeoid'])
            lookup[logrecno] = geos[affgeoid] if affgeoid in geos else None

        except ValueError:
            lookup[logrecno] = None

    print('🌎', 'Lookup generated!')
    return lookup


@sync_to_async
def bulk_create(census_values):
    print("bulk_create")
    return CensusValue.objects.bulk_create([CensusValue(**cv) for cv in census_values])


async def insert_seq_data(seq_no, geo_lookup):
    print("insert_seq_data")
    # prepare geo_lookup connection
    template_file = f'seq{seq_no}.xlsx'
    data_fname = f'{ACS_YEAR}5{ST}{int(seq_no):04}000.txt'

    for dl_dir in (TRACT_BG_DL_DIR, OTHER_GEO_DL_DIR,):
        # estimates and margins of errors in are in separate files
        for mode in ('e', 'm',):
            data_file = os.path.join(dl_dir, f'{mode}{data_fname}')
            census_tables = await extract_variable_data(os.path.join(TEMPLATES_DL_DIR, template_file), mode=mode)
            # open data file and read rows
            with open(data_file) as f:
                print('📄', data_file)
                reader = csv.reader(f)
                census_values = []  # all census values pulled from the current data_file
                for row in reader:
                    new_census_values = await census_values_from_row(row, census_tables, seq_no, mode, geo_lookup)
                    census_values += new_census_values

                # only block to dump data once per file
                await bulk_create(census_values)


async def run_async(start, end, redownload=False, skip_downloads=False, year=None,
                    sequence_numbers=DEFAULT_SEQUENCE_NUMBERS):
    print("run_async")

    for new_dir in (TRACT_BG_DL_DIR, OTHER_GEO_DL_DIR,):
        if not os.path.isdir(new_dir):
            os.makedirs(new_dir)

    geo_lookup = await get_geo_lookup()
    sequence_numbers = (x for x in range(start, end))

    # download data files
    if not skip_downloads:
        # connect to server
        ftp = FTP(FTP_HOST)
        ftp.login()
        await download_data(ftp, redownload, year)

    # join data to columns in templates
    await asyncio.gather(
        *(insert_seq_data(seq_no, geo_lookup) for seq_no in sequence_numbers)
    )


def run(start, end, redownload, skip_downloads, delete, year):
    # ADD YEAR
    print("run")
    if delete:
        CensusValue.objects.all().delete()
        CensusTable.objects.all().delete()
    asyncio.run(run_async(start, end, redownload, skip_downloads, year))
