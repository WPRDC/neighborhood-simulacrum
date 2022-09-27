# Generated by Django 3.2 on 2022-08-31 00:43

import django.contrib.gis.db.models.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='PropertyAssessmentAppeals',
            fields=[
                ('field_id', models.AutoField(db_column='_id', primary_key=True, serialize=False)),
                ('field_full_text', models.TextField(blank=True, db_column='_full_text', null=True)),
                ('parcel_id', models.TextField(blank=True, db_column='PARCEL ID', null=True)),
                ('tax_year', models.TextField(blank=True, db_column='TAX YEAR', null=True)),
                ('class_field', models.TextField(blank=True, db_column='CLASS', null=True)),
                ('class_group', models.TextField(blank=True, db_column='CLASS GROUP', null=True)),
                ('tax_status', models.TextField(blank=True, db_column='TAX_STATUS', null=True)),
                ('muni_code', models.TextField(blank=True, db_column='MUNI_CODE', null=True)),
                ('muni_name', models.TextField(blank=True, db_column='MUNI_NAME', null=True)),
                ('school_code', models.TextField(blank=True, db_column='SCHOOL_CODE', null=True)),
                ('school_district', models.TextField(blank=True, db_column='SCHOOL_DISTRICT', null=True)),
                ('hearing_type', models.TextField(blank=True, db_column='HEARING_TYPE', null=True)),
                ('complainant', models.TextField(blank=True, db_column='COMPLAINANT', null=True)),
                ('hearing_status', models.TextField(blank=True, db_column='HEARING_STATUS', null=True)),
                ('status', models.TextField(blank=True, db_column='STATUS', null=True)),
                ('pre_appeal_land', models.TextField(blank=True, db_column='PRE APPEAL LAND', null=True)),
                ('pre_appeal_bldg', models.TextField(blank=True, db_column='PRE APPEAL BLDG', null=True)),
                ('pre_appeal_total', models.TextField(blank=True, db_column='PRE APPEAL TOTAL', null=True)),
                ('post_appeal_land', models.TextField(blank=True, db_column='POST APPEAL LAND', null=True)),
                ('post_appeal_bldg', models.TextField(blank=True, db_column='POST APPEAL BLDG', null=True)),
                ('post_appeal_total', models.TextField(blank=True, db_column='POST APPEAL TOTAL', null=True)),
                ('hearing_change_amount', models.TextField(blank=True, db_column='HEARING CHANGE AMOUNT', null=True)),
                ('last_update_reason', models.TextField(blank=True, db_column='LAST UPDATE REASON', null=True)),
                ('current_land_value', models.TextField(blank=True, db_column='CURRENT LAND VALUE', null=True)),
                ('current_bldg_value', models.TextField(blank=True, db_column='CURRENT BLDG VALUE', null=True)),
                ('current_total_value', models.TextField(blank=True, db_column='CURRENT TOTAL VALUE', null=True)),
                ('current_value_vs_pre_appeal', models.TextField(blank=True, db_column='CURRENT VALUE vs PRE APPEAL', null=True)),
                ('hearing_date', models.TextField(blank=True, db_column='HEARING DATE', null=True)),
                ('dispo_date', models.TextField(blank=True, db_column='DISPO DATE', null=True)),
                ('elapsed_days', models.TextField(blank=True, db_column='ELAPSED_DAYS', null=True)),
            ],
            options={
                'db_table': 'cb6a8441-0ed9-443d-aea1-a68e62f9a267',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='PropertyAssessments',
            fields=[
                ('field_id', models.AutoField(db_column='_id', primary_key=True, serialize=False)),
                ('field_full_text', models.TextField(blank=True, db_column='_full_text', null=True)),
                ('parid', models.TextField(blank=True, db_column='PARID', null=True, unique=True)),
                ('propertyhousenum', models.TextField(blank=True, db_column='PROPERTYHOUSENUM', null=True)),
                ('propertyfraction', models.TextField(blank=True, db_column='PROPERTYFRACTION', null=True)),
                ('propertyaddress', models.TextField(blank=True, db_column='PROPERTYADDRESS', null=True)),
                ('propertycity', models.TextField(blank=True, db_column='PROPERTYCITY', null=True)),
                ('propertystate', models.TextField(blank=True, db_column='PROPERTYSTATE', null=True)),
                ('propertyunit', models.TextField(blank=True, db_column='PROPERTYUNIT', null=True)),
                ('propertyzip', models.TextField(blank=True, db_column='PROPERTYZIP', null=True)),
                ('municode', models.TextField(blank=True, db_column='MUNICODE', null=True)),
                ('munidesc', models.TextField(blank=True, db_column='MUNIDESC', null=True)),
                ('schoolcode', models.TextField(blank=True, db_column='SCHOOLCODE', null=True)),
                ('schooldesc', models.TextField(blank=True, db_column='SCHOOLDESC', null=True)),
                ('legal1', models.TextField(blank=True, db_column='LEGAL1', null=True)),
                ('legal2', models.TextField(blank=True, db_column='LEGAL2', null=True)),
                ('legal3', models.TextField(blank=True, db_column='LEGAL3', null=True)),
                ('neighcode', models.TextField(blank=True, db_column='NEIGHCODE', null=True)),
                ('neighdesc', models.TextField(blank=True, db_column='NEIGHDESC', null=True)),
                ('taxcode', models.TextField(blank=True, db_column='TAXCODE', null=True)),
                ('taxdesc', models.TextField(blank=True, db_column='TAXDESC', null=True)),
                ('taxsubcode', models.TextField(blank=True, db_column='TAXSUBCODE', null=True)),
                ('taxsubcode_desc', models.TextField(blank=True, db_column='TAXSUBCODE_DESC', null=True)),
                ('ownercode', models.TextField(blank=True, db_column='OWNERCODE', null=True)),
                ('ownerdesc', models.TextField(blank=True, db_column='OWNERDESC', null=True)),
                ('class_field', models.TextField(blank=True, db_column='CLASS', null=True)),
                ('classdesc', models.TextField(blank=True, db_column='CLASSDESC', null=True)),
                ('usecode', models.TextField(blank=True, db_column='USECODE', null=True)),
                ('usedesc', models.TextField(blank=True, db_column='USEDESC', null=True)),
                ('lotarea', models.FloatField(blank=True, db_column='LOTAREA', null=True)),
                ('homesteadflag', models.TextField(blank=True, db_column='HOMESTEADFLAG', null=True)),
                ('cleangreen', models.TextField(blank=True, db_column='CLEANGREEN', null=True)),
                ('farmsteadflag', models.TextField(blank=True, db_column='FARMSTEADFLAG', null=True)),
                ('abatementflag', models.TextField(blank=True, db_column='ABATEMENTFLAG', null=True)),
                ('recorddate', models.TextField(blank=True, db_column='RECORDDATE', null=True)),
                ('saledate', models.TextField(blank=True, db_column='SALEDATE', null=True)),
                ('saleprice', models.FloatField(blank=True, db_column='SALEPRICE', null=True)),
                ('salecode', models.TextField(blank=True, db_column='SALECODE', null=True)),
                ('saledesc', models.TextField(blank=True, db_column='SALEDESC', null=True)),
                ('deedbook', models.TextField(blank=True, db_column='DEEDBOOK', null=True)),
                ('deedpage', models.TextField(blank=True, db_column='DEEDPAGE', null=True)),
                ('prevsaledate', models.TextField(blank=True, db_column='PREVSALEDATE', null=True)),
                ('prevsaleprice', models.FloatField(blank=True, db_column='PREVSALEPRICE', null=True)),
                ('prevsaledate2', models.TextField(blank=True, db_column='PREVSALEDATE2', null=True)),
                ('prevsaleprice2', models.FloatField(blank=True, db_column='PREVSALEPRICE2', null=True)),
                ('changenoticeaddress1', models.TextField(blank=True, db_column='CHANGENOTICEADDRESS1', null=True)),
                ('changenoticeaddress2', models.TextField(blank=True, db_column='CHANGENOTICEADDRESS2', null=True)),
                ('changenoticeaddress3', models.TextField(blank=True, db_column='CHANGENOTICEADDRESS3', null=True)),
                ('changenoticeaddress4', models.TextField(blank=True, db_column='CHANGENOTICEADDRESS4', null=True)),
                ('countybuilding', models.FloatField(blank=True, db_column='COUNTYBUILDING', null=True)),
                ('countyland', models.FloatField(blank=True, db_column='COUNTYLAND', null=True)),
                ('countytotal', models.FloatField(blank=True, db_column='COUNTYTOTAL', null=True)),
                ('countyexemptbldg', models.FloatField(blank=True, db_column='COUNTYEXEMPTBLDG', null=True)),
                ('localbuilding', models.FloatField(blank=True, db_column='LOCALBUILDING', null=True)),
                ('localland', models.FloatField(blank=True, db_column='LOCALLAND', null=True)),
                ('localtotal', models.FloatField(blank=True, db_column='LOCALTOTAL', null=True)),
                ('fairmarketbuilding', models.FloatField(blank=True, db_column='FAIRMARKETBUILDING', null=True)),
                ('fairmarketland', models.FloatField(blank=True, db_column='FAIRMARKETLAND', null=True)),
                ('fairmarkettotal', models.FloatField(blank=True, db_column='FAIRMARKETTOTAL', null=True)),
                ('style', models.TextField(blank=True, db_column='STYLE', null=True)),
                ('styledesc', models.TextField(blank=True, db_column='STYLEDESC', null=True)),
                ('stories', models.TextField(blank=True, db_column='STORIES', null=True)),
                ('yearblt', models.FloatField(blank=True, db_column='YEARBLT', null=True)),
                ('exteriorfinish', models.TextField(blank=True, db_column='EXTERIORFINISH', null=True)),
                ('extfinish_desc', models.TextField(blank=True, db_column='EXTFINISH_DESC', null=True)),
                ('roof', models.TextField(blank=True, db_column='ROOF', null=True)),
                ('roofdesc', models.TextField(blank=True, db_column='ROOFDESC', null=True)),
                ('basement', models.TextField(blank=True, db_column='BASEMENT', null=True)),
                ('basementdesc', models.TextField(blank=True, db_column='BASEMENTDESC', null=True)),
                ('grade', models.TextField(blank=True, db_column='GRADE', null=True)),
                ('gradedesc', models.TextField(blank=True, db_column='GRADEDESC', null=True)),
                ('condition', models.TextField(blank=True, db_column='CONDITION', null=True)),
                ('conditiondesc', models.TextField(blank=True, db_column='CONDITIONDESC', null=True)),
                ('cdu', models.TextField(blank=True, db_column='CDU', null=True)),
                ('cdudesc', models.TextField(blank=True, db_column='CDUDESC', null=True)),
                ('totalrooms', models.FloatField(blank=True, db_column='TOTALROOMS', null=True)),
                ('bedrooms', models.FloatField(blank=True, db_column='BEDROOMS', null=True)),
                ('fullbaths', models.FloatField(blank=True, db_column='FULLBATHS', null=True)),
                ('halfbaths', models.FloatField(blank=True, db_column='HALFBATHS', null=True)),
                ('heatingcooling', models.TextField(blank=True, db_column='HEATINGCOOLING', null=True)),
                ('heatingcoolingdesc', models.TextField(blank=True, db_column='HEATINGCOOLINGDESC', null=True)),
                ('fireplaces', models.FloatField(blank=True, db_column='FIREPLACES', null=True)),
                ('bsmtgarage', models.TextField(blank=True, db_column='BSMTGARAGE', null=True)),
                ('finishedlivingarea', models.FloatField(blank=True, db_column='FINISHEDLIVINGAREA', null=True)),
                ('cardnumber', models.FloatField(blank=True, db_column='CARDNUMBER', null=True)),
                ('alt_id', models.TextField(blank=True, db_column='ALT_ID', null=True)),
                ('taxyear', models.FloatField(blank=True, db_column='TAXYEAR', null=True)),
                ('asofdate', models.DateField(blank=True, db_column='ASOFDATE', null=True)),
                ('municipality', models.TextField(blank=True, db_column='MUNICIPALITY', null=True)),
                ('neighborhood', models.TextField(blank=True, db_column='NEIGHBORHOOD', null=True)),
                ('pgh_council_district', models.TextField(blank=True, db_column='PGH_COUNCIL_DISTRICT', null=True)),
                ('pgh_ward', models.TextField(blank=True, db_column='PGH_WARD', null=True)),
                ('pgh_public_works_division', models.TextField(blank=True, db_column='PGH_PUBLIC_WORKS_DIVISION', null=True)),
                ('pgh_police_zone', models.TextField(blank=True, db_column='PGH_POLICE_ZONE', null=True)),
                ('pgh_fire_zone', models.TextField(blank=True, db_column='PGH_FIRE_ZONE', null=True)),
                ('tract', models.TextField(blank=True, db_column='TRACT', null=True)),
                ('block_group', models.TextField(blank=True, db_column='BLOCK_GROUP', null=True)),
                ('field_geom', django.contrib.gis.db.models.fields.PointField(blank=True, db_column='_geom', null=True, srid=4326)),
                ('field_the_geom_webmercator', django.contrib.gis.db.models.fields.PointField(blank=True, db_column='_the_geom_webmercator', null=True, srid=3857)),
            ],
            options={
                'db_table': '518b583f-7cc8-4f60-94d0-174cc98310dc',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='PropertySales',
            fields=[
                ('field_id', models.AutoField(db_column='_id', primary_key=True, serialize=False)),
                ('field_full_text', models.TextField(blank=True, db_column='_full_text', null=True)),
                ('parid', models.TextField(blank=True, db_column='PARID', null=True)),
                ('propertyhousenum', models.IntegerField(blank=True, db_column='PROPERTYHOUSENUM', null=True)),
                ('propertyfraction', models.TextField(blank=True, db_column='PROPERTYFRACTION', null=True)),
                ('propertyaddressdir', models.TextField(blank=True, db_column='PROPERTYADDRESSDIR', null=True)),
                ('propertyaddressstreet', models.TextField(blank=True, db_column='PROPERTYADDRESSSTREET', null=True)),
                ('propertyaddresssuf', models.TextField(blank=True, db_column='PROPERTYADDRESSSUF', null=True)),
                ('propertyaddressunitdesc', models.TextField(blank=True, db_column='PROPERTYADDRESSUNITDESC', null=True)),
                ('propertyunitno', models.TextField(blank=True, db_column='PROPERTYUNITNO', null=True)),
                ('propertycity', models.TextField(blank=True, db_column='PROPERTYCITY', null=True)),
                ('propertystate', models.TextField(blank=True, db_column='PROPERTYSTATE', null=True)),
                ('propertyzip', models.FloatField(blank=True, db_column='PROPERTYZIP', null=True)),
                ('schoolcode', models.TextField(blank=True, db_column='SCHOOLCODE', null=True)),
                ('schooldesc', models.TextField(blank=True, db_column='SCHOOLDESC', null=True)),
                ('municode', models.TextField(blank=True, db_column='MUNICODE', null=True)),
                ('munidesc', models.TextField(blank=True, db_column='MUNIDESC', null=True)),
                ('recorddate', models.DateField(blank=True, db_column='RECORDDATE', null=True)),
                ('saledate', models.DateField(blank=True, db_column='SALEDATE', null=True)),
                ('price', models.FloatField(blank=True, db_column='PRICE', null=True)),
                ('deedbook', models.TextField(blank=True, db_column='DEEDBOOK', null=True)),
                ('deedpage', models.TextField(blank=True, db_column='DEEDPAGE', null=True)),
                ('salecode', models.TextField(blank=True, db_column='SALECODE', null=True)),
                ('saledesc', models.TextField(blank=True, db_column='SALEDESC', null=True)),
                ('instrtyp', models.TextField(blank=True, db_column='INSTRTYP', null=True)),
                ('instrtypdesc', models.TextField(blank=True, db_column='INSTRTYPDESC', null=True)),
                ('field_geom', django.contrib.gis.db.models.fields.PointField(blank=True, db_column='_geom', null=True, srid=4326)),
                ('field_the_geom_webmercator', django.contrib.gis.db.models.fields.PointField(blank=True, db_column='_the_geom_webmercator', null=True, srid=3857)),
            ],
            options={
                'db_table': '5bbe6c55-bce6-4edb-9d04-68edeb6bf7b1',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Parcel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('parcel_id', models.CharField(max_length=24)),
                ('house_number', models.CharField(blank=True, max_length=20, null=True)),
                ('street_name', models.CharField(blank=True, max_length=60, null=True)),
                ('city', models.CharField(blank=True, max_length=60, null=True)),
                ('state', models.CharField(blank=True, max_length=60, null=True)),
                ('zip_code', models.CharField(blank=True, max_length=60, null=True)),
                ('landmark_name', models.CharField(blank=True, max_length=60, null=True)),
                ('post_box', models.CharField(blank=True, max_length=100, null=True)),
                ('building_name', models.CharField(blank=True, max_length=60, null=True)),
            ],
        ),
    ]
