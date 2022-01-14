"""
Script to load census and acs data into our models.

Some notes about the data formats and weirdness of it can be found here:
https://www2.census.gov/programs-surveys/acs/summary_file/2019/documentation/tech_docs/ACS_SF_Excel_Import_Tool.pdf

"""
import csv
import json
import os
import zipfile
from ftplib import FTP
from functools import lru_cache
from typing import List

import pandas as pd
import requests
from asgiref.sync import sync_to_async
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from openpyxl import load_workbook

from census_data.models import CensusValue, CensusTableRecord
from geo.models import AdminRegion

COUNTIES = ('42073', '42003', '42007', '42125', '42059',
            '42051', '42129', '42063', '42005', '42019',)

DEFAULT_SEQUENCE_NUMBERS = ('3',)

STATE = 'Pennsylvania'  # in PascalCase, e.g. New Mexico is NewMexico
ST = 'pa'  # state abbreviation in lowercase

FIVE_YEAR_DIRNAME = '5_year_seq_by_state'

TRACT_DIRNAME = 'Tracts_Block_Groups_Only'
OTHER_GEO_DIRNAME = 'All_Geographies_Not_Tracts_Block_Groups'

TEMPLATE_FILENAME = '2019_5yr_Summary_FileTemplates.zip'

FTP_HOST = 'ftp2.census.gov'

# https://www.census.gov/programs-surveys/geography/technical-documentation/naming-convention/cartographic-boundary-file/carto-boundary-summary-level.html
SUMMARY_LEVELS = {'050', '060', '140', '150', '860', '970'}
SUMMARY_LEVELS_SF1 = {'050', '060', '140', '150', '871', '970'}


# Utilities
# -*-*-*-*-
def get_ftp_data_dir(year):
    return f'/programs-surveys/acs/summary_file/{year}/data/'


def get_base_ftp_dir(year):
    return f'/programs-surveys/acs/summary_file/{year}/data/5_year_seq_by_state/{STATE}'


def get_base_dl_dir(year):
    base_dir = ensure_path(os.path.join(settings.BASE_DIR, 'data', 'acs5'))
    return ensure_path(os.path.join(base_dir, str(year)))


def get_ftp_dirs(year):
    base_dir = get_base_ftp_dir(year)
    tract_dir = f'{base_dir}/{TRACT_DIRNAME}'
    other_dir = f'{base_dir}/{OTHER_GEO_DIRNAME}'
    return tract_dir, other_dir


def get_dl_dirs(year):
    base_dir = get_base_dl_dir(year)
    tract_dir = ensure_path(os.path.join(base_dir, TRACT_DIRNAME.lower()))
    other_dir = ensure_path(os.path.join(base_dir, OTHER_GEO_DIRNAME.lower()))
    return tract_dir, other_dir


def get_template_dirs(year) -> object:
    base_ftp_dir = get_base_ftp_dir(year)
    ftp_dir = f'{base_ftp_dir}/{year}/'

    base_dl_dir = ensure_path(os.path.join(settings.BASE_DIR, 'data', 'acs5'))
    dl_dir = ensure_path(os.path.join(base_dl_dir, str(year)))

    return ftp_dir, dl_dir


@lru_cache
def format_affgeoid(affgeoid):
    parts = affgeoid.split('US')
    try:
        result = f'{int(parts[0]):05}00US{parts[1]}'
    except ValueError:
        result = affgeoid
    return result


@lru_cache
def ensure_path(path) -> str:
    if not os.path.isdir(path):
        os.mkdir(path)
    return path


def already_exists(dl_dir, data_file):
    return (os.path.isfile(os.path.join(dl_dir, f'e{data_file[:-4]}.txt'))
            and os.path.isfile(os.path.join(dl_dir, f'm{data_file[:-4]}.txt')))


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


# Geo lookup
# -*-*-*-*-*-
def get_or_make_geo_lookup(year: int, redownload=False) -> dict:
    """ Generate a lookup table that maps the geoids we use to the record numbers in the data """
    data_dir = ensure_path(os.path.join(settings.BASE_DIR, 'data'))
    lookup_dir = ensure_path(os.path.join(data_dir, 'geo_lookups'))
    file_name_base = os.path.join(lookup_dir, f'{year}{ST}')
    dl_fname = f'{file_name_base}.xlsx'
    lookup_fname = f'{file_name_base}.json'
    print('🌏', 'Generating geo lookup ')
    # first check if a cached lookup exists
    if redownload or os.path.isfile(lookup_fname):
        print('  ', '✅️', 'Cache hit.', f'Returning look found at {lookup_fname}')
        with open(lookup_fname) as f:
            return json.load(f)
    else:
        print('  ', '❌', 'Cache miss.', 'Preceding to generate lookup')

    # download geography file if necessary
    if not os.path.isfile(dl_fname):
        print('📡', 'Downloading geo file... ', end='')
        r = requests.get(
            f'https://www2.census.gov/programs-surveys/acs/summary_file/{year}/documentation/geography/5yr_year_geo/{ST}.xlsx'
        )
        with open(dl_fname, 'wb') as output:
            output.write(r.content)
        print(' Done!')
    else:
        print('⤵️️', 'Skipping download.', 'Source file already exists.')

    print('⛏', 'Extracting data...')
    df = pd.read_excel(dl_fname)

    log_rec_df = pd.DataFrame()
    log_rec_df['logrecno'] = df['Logical Record Number']
    log_rec_df['affgeoid'] = df['Geography ID'].map(format_affgeoid)

    # get array of data ([logrecno: str, affeoid][])
    data: List[List[str]] = log_rec_df.to_dict(orient='split')['data']

    lookup = {f'{datum[0]:07}': datum[1] for datum in data}
    print('🌎', 'Lookup generated!')

    # save cached version
    with open(lookup_fname, 'w') as f:
        json.dump(lookup, f)

    return lookup


def get_or_make_census_geo_lookup(year: int, redownload=False) -> dict:
    data_dir = ensure_path(os.path.join(settings.BASE_DIR, 'data'))
    lookup_dir = ensure_path(os.path.join(data_dir, 'geo_lookups'))
    lookup_filename = os.path.join(lookup_dir, f'cen_{year}.json')
    source_filename = os.path.join(lookup_dir, f'{ST}geo{year}.sf1')

    # first check if a cached lookup exists
    if os.path.isfile(lookup_filename):
        print('  ', '✅️', 'Cache hit.', f'Returning look found at {lookup_filename}')
        with open(lookup_filename) as f:
            return json.load(f)
    else:
        print('  ', '❌', 'Cache miss.', 'Preceding to generate lookup')
    lookup = {}
    # read source file
    with open(source_filename) as f:
        for line in f.readlines():
            summary_level = line[8:11]
            # limit to select geographies
            if summary_level not in SUMMARY_LEVELS_SF1:
                continue

            logrecno = line[18:25]
            state = line[27:29]
            county = line[29:32]

            # limit to the app's extent
            if county not in settings.AVAILABLE_COUNTIES_IDS:
                continue

            # extract geo id parts from the data see fig 2-5 in the docs
            # http://www2.census.gov/programs-surveys/decennial/2010/technical-documentation/complete-tech-docs/summary-file/sf1.pdf
            countysub = line[36:41]
            tract = line[54:60]
            blockgrp = line[60:61]
            # block = line[61:65]
            zcta = line[171:176]
            school_district_u = line[194:199]

            name = line[226:316].strip()

            geoid = ''
            if summary_level == '050':  # county
                geoid = state + county
            if summary_level == '060':  # county subdivision
                geoid = state + county + countysub
            if summary_level == '140':  # tract
                geoid = state + county + tract
            if summary_level == '150':  # block group
                geoid = state + county + tract + blockgrp
            if summary_level == '871':  # zip code
                geoid = zcta
            if summary_level == '970':  # school district (unified)
                geoid = school_district_u

            geoid = geoid.strip()
            affgeoid = summary_level + '0000US' + geoid

            print(geoid, affgeoid, name)
            lookup[logrecno] = affgeoid

    # save lookup
    with open(lookup_filename, 'w') as f:
        json.dump(lookup, f)
    return lookup


# Downloading data
# -*-*-*-*-*-*-*-*-
def download(ftp, dl_dir, data_file):
    print('  ⬇️️', 'Downloading', data_file, end='')
    dl_path = os.path.join(dl_dir, data_file)
    with open(dl_path, 'wb') as f:
        ftp.retrbinary(f'RETR {data_file}', f.write)
        print('.', end='')
    # extract files
    with zipfile.ZipFile(dl_path, 'r') as zf:
        zf.extractall(dl_dir)
        print('.', end='')
    # delete zip
    os.remove(dl_path)
    print('. Done!')


def is_file_for_seq_no(data_file, seq_no):
    return seq_no == int(data_file[7:11])


def download_acs5_data(seq_no, year, redownload=False):
    tract_bg_ftp_dir, other_geo_ftp_dir = get_ftp_dirs(year)
    tract_bg_dl_dir, other_geo_dl_dir = get_dl_dirs(year)

    tract_bg_dir_pair = (tract_bg_ftp_dir, tract_bg_dl_dir)
    other_geo_dir_pair = (other_geo_ftp_dir, other_geo_dl_dir)

    ftp = FTP(FTP_HOST)
    ftp.login()

    # the data for geographies is split across two files
    for (data_dir, dl_dir) in (tract_bg_dir_pair, other_geo_dir_pair,):
        ftp.cwd(data_dir)
        data_files = ftp.nlst()
        for data_file in data_files:
            # skip the other file(s)
            if data_file[-3:] != 'zip':
                # print('  ', '🙈 Ignoring', data_file)
                continue

            if not is_file_for_seq_no(data_file, seq_no):
                # print('  ', '🙈 Ignoring', data_file, 'Not in range.')
                continue

            if redownload or not already_exists(dl_dir, data_file):
                download(ftp, dl_dir, data_file)
        # print('  ', '⤵', 'Skipping', data_file)

    # download template file zip if necessary
    template_ftp_dir = get_ftp_data_dir(year)
    template_dl_dir = get_base_dl_dir(year)
    template_dl_path = os.path.join(template_dl_dir, TEMPLATE_FILENAME)
    if redownload or not os.path.isfile(template_dl_path):
        print('⬇️', f'Downloading template files')
        print(f'  from: {template_ftp_dir}/{TEMPLATE_FILENAME}')
        print(f'    to: {template_dl_path}')

        with open(template_dl_path, 'wb') as f:
            ftp.retrbinary(f'RETR {template_ftp_dir}/{TEMPLATE_FILENAME}', f.write)

        with zipfile.ZipFile(template_dl_path, 'r') as zf:
            zf.extractall(template_dl_dir)
    else:
        print('✅', f'Template file found at {template_dl_path}.')


def download_census_data(year, redownload=False):
    file_name = f'{ST}{year}.sf1.zip'

    data_dir = ensure_path(os.path.join(settings.BASE_DIR, 'data'))
    dl_dir = ensure_path(os.path.join(data_dir, f'cen_{year}'))  # /data/cen_2010/
    dl_filename = ensure_path(os.path.join(dl_dir, file_name))  # /data/cen_2010/ps2010.sf1.zip

    ftp = FTP(FTP_HOST)
    ftp.login()
    with open(dl_filename, 'wb') as f:
        ftp.retrbinary(f'RETR /census_2010/04-Summary_File_1/Pennsylvania/{file_name}', f.write)

    with zipfile.ZipFile(dl_filename, 'r') as zf:
        zf.extractall(dl_filename)


def extract_table_details(seq_no, year, fname) -> List['CensusTableRecord']:
    tables = []
    wb = load_workbook(filename=fname)

    # col 6 is when the real data starts
    for i in range(6, len(wb['e'][1])):
        table_id = wb['e'][1][i].value
        value_id = table_id + 'E'
        moe_id = table_id + 'M'
        desc = wb['e'][2][i].value
        census_table = CensusTableRecord(
            table_id=table_id, description=desc,
            year=year, dataset='ACS5',
        )
        tables.append(census_table)

    print(f'({seq_no})', f'{len(tables)} Tables found.')
    return tables


# Saving Data
# -*-*-*-*-*-
def census_values_from_row(row, census_tables, seq_no, mode, geo_lookup) -> List['CensusValue']:
    census_values = []
    logrecno = row[5]
    affgeoid: str = geo_lookup[logrecno]

    # Only use certain geos
    if not affgeoid:
        # print('❌ not found')
        return []
    if affgeoid.split('US')[1][:5] not in COUNTIES:
        # print('⤵️', affgeoid, affgeoid, 'out of range')
        return []
    if affgeoid[:3] not in SUMMARY_LEVELS:
        return []

    # print('🏙', affgeoid, f'[{seq_no}{mode.upper()}]')

    # for the cells that have data in them
    for i in range(6, len(row)):
        cell = row[i]
        census_table = census_tables[i - 6]
        # Get value
        try:
            value = float(cell)
        except ValueError:
            value = None

        new_cv = {'geog_uid': affgeoid,
                  'census_table_uid': census_table.uid,
                  'value': value,
                  'raw_value': cell}
        census_values.append(new_cv)

    return [CensusValue(**cv) for cv in census_values]


def insert_seq_data(seq_no, year, geo_lookup):
    # prepare geo_lookup connection
    template_file = f'seq{seq_no}.xlsx'
    data_fname = f'{year}5{ST}{int(seq_no):04}000.txt'
    _, year_dir = get_template_dirs(year)

    # make sure CensusTable objects are created
    census_tables = extract_table_details(
        seq_no,
        year,
        os.path.join(year_dir, template_file),
    )
    print('🚚', f'({seq_no})', 'Uploading tables')
    CensusTableRecord.objects.bulk_create(census_tables, ignore_conflicts=True)
    return
    # extract data from all the data files
    census_values = []
    for dl_dir in get_dl_dirs(year):  # for ACS this ends up being two directories
        # estimates and margins of errors in are in separate files
        for mode in ('e', 'm',):
            data_file = os.path.join(dl_dir, f'{mode}{data_fname}')
            # open data file and read rows
            with open(data_file) as f:
                print('📄', f'Extracting data from "{mode}{data_fname}"')
                reader = csv.reader(f)
                for row in reader:
                    new_census_values = census_values_from_row(row, tables_for_mode, seq_no, mode, geo_lookup)
                    census_values += new_census_values

    # fixme: this is the bottleneck on a fast machine and can be further optimized
    #   postgres and django probably each have some tips on what to do
    print('🚛️', f'({seq_no})', 'Uploading values')
    CensusValue.objects.bulk_create(census_values, ignore_conflicts=True)


def run_for_seq_no(seq_no, year, lookup, redownload):
    print('🚦', f'Starting job for {seq_no}.')
    download_acs5_data(seq_no, year, redownload=redownload)
    insert_seq_data(seq_no, year, lookup)


def run(start, end, year=2019, redownload=False, delete=False):
    if delete:
        print("DELETING DISABLED")
        # print('🗑', 'Deleting old Census objects first...')
        # CensusValue.objects.all().delete()
        # CensusTable.objects.all().delete()

    lookup = get_or_make_geo_lookup(year)

    for seq_no in range(start, end + 1):
        run_for_seq_no(seq_no, year, lookup, redownload)
