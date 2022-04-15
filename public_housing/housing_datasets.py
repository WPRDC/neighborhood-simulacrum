from django.contrib.gis.db import models

from profiles.abstract_models import DatastoreDataset


class LookupTable(DatastoreDataset):
    projectidentifier_id = models.CharField(max_length=100)
    projectindex_id = models.CharField(max_length=100)

    class Meta:
        abstract = True


class ContractID(LookupTable):
    class Meta:
        managed = False
        db_table = 'ba6b156f-82fe-41b0-83b9-c17540836598'


class DevelopmentCode(LookupTable):
    class Meta:
        managed = False
        db_table = '25c0e399-0ad8-42cf-8899-e6f35faf1187'


class FHALoanID(LookupTable):
    class Meta:
        managed = False
        db_table = '64449027-404c-48fb-a9a4-75e9e8d14188'


class LIHTCProjectID(LookupTable):
    class Meta:
        managed = False
        db_table = 'e5b27187-b134-4050-8101-db4e19ffdb30'


class NormalizeStateID(LookupTable):
    class Meta:
        managed = False
        db_table = 'f71eb9f3-c413-47a3-8592-af447fe93020'


class PMIndx(LookupTable):
    class Meta:
        managed = False
        db_table = '6234dd27-79f4-43d3-b098-19f12692ce55'


# These are directly tied to datasets on the datacenter's CKAN datastore
# The table names are the datasets' CKAN resource IDs.
class HousingDataset(DatastoreDataset):
    """ Abstract base class mainly used for typing """
    hc_index_fields: tuple[str]

    class Meta:
        abstract = True


class HouseCatSubsidyListing(HousingDataset):
    property_id = models.TextField(blank=True, null=True)
    subsidy_data_source = models.TextField(blank=True, null=True)
    hud_property_name = models.TextField(blank=True, null=True)
    subsidy_expiration_date = models.DateField()

    hc_index_fields = ('property_id',)

    class Meta:
        managed = False
        db_table = '6803b4c9-df5d-4ef0-8c33-43e9feaff0a2'


class ActiveHUDMultifamilyInsuredMortgages(HousingDataset):
    fha_loan_id = models.TextField(blank=True, null=True)

    full_text = models.TextField(db_column='_full_text', blank=True, null=True)
    hud_property_name = models.TextField(blank=True, null=True)
    property_street_address = models.TextField(blank=True, null=True)
    city = models.TextField(blank=True, null=True)
    state = models.TextField(blank=True, null=True)
    zip_code = models.TextField(blank=True, null=True)
    units = models.IntegerField(blank=True, null=True)
    initial_endorsement_date = models.DateField(blank=True, null=True)
    original_mortgage_amount = models.IntegerField(blank=True, null=True)
    maturity_date = models.DateField(blank=True, null=True)
    term_in_months = models.IntegerField(blank=True, null=True)
    interest_rate = models.FloatField(blank=True, null=True)
    current_principal_and_interest = models.FloatField(blank=True, null=True)
    amoritized_principal_balance = models.FloatField(blank=True, null=True)
    holder_name = models.TextField(blank=True, null=True)
    holder_city = models.TextField(blank=True, null=True)
    holder_state = models.TextField(blank=True, null=True)
    servicer_name = models.TextField(blank=True, null=True)
    servicer_city = models.TextField(blank=True, null=True)
    servicer_state = models.TextField(blank=True, null=True)
    section_of_act_code = models.TextField(blank=True, null=True)
    program_category = models.TextField(blank=True, null=True)
    geom = models.PointField(db_column='_geom', blank=True, null=True)
    geom_webmercator = models.PointField(db_column='_the_geom_webmercator', srid=3857, blank=True, null=True)

    hc_index_fields = ('fha_loan_id',)

    class Meta:
        managed = False
        db_table = '931d45da-f791-46c4-998b-60bafa904b36'


class HUDMultifamilyFiscalYearProduction(HousingDataset):
    fha_loan_id = models.TextField(blank=True, null=True)

    full_text = models.TextField(db_column='_full_text', blank=True, null=True)
    hud_property_name = models.TextField(blank=True, null=True)
    city = models.TextField(blank=True, null=True)
    state = models.TextField(blank=True, null=True)
    initial_endorsement_date = models.DateField(blank=True, null=True)
    original_mortgage_amount = models.IntegerField(blank=True, null=True)
    program_category = models.TextField(blank=True, null=True)
    units = models.IntegerField(blank=True, null=True)
    basic_fha_risk_share_or_other = models.TextField(blank=True, null=True)
    current_status_of_loan = models.TextField(blank=True, null=True)
    date_of_firm_issue = models.DateField(blank=True, null=True)
    firm_commitment_lender = models.TextField(blank=True, null=True)
    holder_name = models.TextField(blank=True, null=True)
    geom = models.PointField(db_column='_geom', blank=True, null=True)
    the_geom_webmercator = models.PointField(db_column='_the_geom_webmercator', srid=3857, blank=True, null=True)

    hc_index_fields = ('fha_loan_id',)

    class Meta:
        managed = False
        db_table = 'b3ff057c-1518-4a34-a004-39d3d49a5ad7'


class LIHTC(HousingDataset):
    lihtc_project_id = models.TextField(blank=True, null=True)
    normalized_state_id = models.TextField(blank=True, null=True)

    full_text = models.TextField(db_column='_full_text', blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    census_tract = models.TextField(blank=True, null=True)
    census_tract_2000 = models.TextField(blank=True, null=True)
    county_fips_code = models.TextField(blank=True, null=True)
    municipality_fips = models.IntegerField(blank=True, null=True)
    hud_property_name = models.TextField(blank=True, null=True)
    property_street_address = models.TextField(blank=True, null=True)
    city = models.TextField(blank=True, null=True)
    state = models.TextField(blank=True, null=True)
    zip_code = models.TextField(blank=True, null=True)
    units = models.IntegerField(blank=True, null=True)
    assisted_units = models.IntegerField(blank=True, null=True)
    count_0br = models.IntegerField(blank=True, null=True)
    count_1br = models.IntegerField(blank=True, null=True)
    count_2br = models.IntegerField(blank=True, null=True)
    count_3br = models.IntegerField(blank=True, null=True)
    count_4br = models.IntegerField(blank=True, null=True)
    federal_id = models.TextField(blank=True, null=True)
    state_id = models.TextField(blank=True, null=True)
    lihtc_credit = models.TextField(blank=True, null=True)
    lihtc_construction_type = models.TextField(blank=True, null=True)
    lihtc_year_allocated = models.IntegerField(blank=True, null=True)
    lihtc_year_in_service = models.IntegerField(blank=True, null=True)
    lihtc_amount = models.TextField(blank=True, null=True)
    fmha_514_loan = models.BooleanField(blank=True, null=True)
    fmha_515_loan = models.BooleanField(blank=True, null=True)
    fmha_538_loan = models.BooleanField(blank=True, null=True)
    scattered_site_ind = models.TextField(blank=True, null=True)
    geom = models.PointField(db_column='_geom', blank=True, null=True)
    geom_webmercator = models.PointField(db_column='_the_geom_webmercator', srid=3857, blank=True, null=True)

    hc_index_fields = ('lihtc_project_id', 'normalized_state_id',)

    class Meta:
        managed = False
        db_table = 'd5275180-13f1-460b-b933-aab6afc2966e'


class AllBuildingsFromLIHTCProjects(HousingDataset):
    lihtc_project_id = models.TextField(blank=True, null=True)
    normalized_state_id = models.TextField(blank=True, null=True)

    full_text = models.TextField(db_column='_full_text', blank=True, null=True)
    hud_property_name = models.TextField(blank=True, null=True)
    property_street_address = models.TextField(blank=True, null=True)
    city = models.TextField(blank=True, null=True)
    state = models.TextField(blank=True, null=True)
    zip_code = models.TextField(blank=True, null=True)
    state_id = models.TextField(blank=True, null=True)
    geom = models.PointField(db_column='_geom', blank=True, null=True)
    geom_webmercator = models.PointField(db_column='_the_geom_webmercator', srid=3857, blank=True, null=True)

    hc_index_fields = ('lihtc_project_id', 'normalized_state_id',)

    class Meta:
        managed = False
        db_table = 'ad49ed19-1122-4f9d-a3c2-491f36a293f4'


class HUDInspectionScores(HousingDataset):
    development_code = models.TextField(blank=True, null=True)

    full_text = models.TextField(db_column='_full_text', blank=True, null=True)
    state = models.TextField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    county = models.TextField(blank=True, null=True)
    county_fips_code = models.TextField(blank=True, null=True)
    hud_property_name = models.TextField(blank=True, null=True)
    property_street_address = models.TextField(blank=True, null=True)
    inspection_id = models.IntegerField(blank=True, null=True)
    inspection_property_id_multiformat = models.TextField(blank=True, null=True)
    inspection_score = models.IntegerField(blank=True, null=True)
    inspection_date = models.DateField(blank=True, null=True)
    participant_code = models.TextField(blank=True, null=True)
    formal_participant_name = models.TextField(blank=True, null=True)
    geom = models.PointField(db_column='_geom', blank=True, null=True)
    geom_webmercator = models.PointField(db_column='_the_geom_webmercator', srid=3857, blank=True, null=True)

    hc_index_fields = ('development_code',)

    class Meta:
        managed = False
        db_table = 'a768bb6b-9d1e-463f-9711-651fedf971fb'
        ordering = ['-inspection_date']

class HUDPublicHousingDevelopments(HousingDataset):
    development_code = models.TextField(blank=True, null=True)

    full_text = models.TextField(db_column='_full_text', blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    geocoding_accuracy = models.TextField(blank=True, null=True)
    county_fips_code = models.TextField(blank=True, null=True)
    census_tract = models.TextField(blank=True, null=True)
    municipality_fips = models.TextField(blank=True, null=True)
    municipality_name = models.TextField(blank=True, null=True)
    hud_property_name = models.TextField(blank=True, null=True)
    property_street_address = models.TextField(blank=True, null=True)
    city = models.TextField(blank=True, null=True)
    state = models.TextField(blank=True, null=True)
    zip_code = models.TextField(blank=True, null=True)
    units = models.IntegerField(blank=True, null=True)
    owner_organization_name = models.TextField(blank=True, null=True)
    participant_code = models.TextField(blank=True, null=True)
    formal_participant_name = models.TextField(blank=True, null=True)
    project_name = models.TextField(blank=True, null=True)
    total_dwelling_units = models.IntegerField(blank=True, null=True)
    acc_units = models.IntegerField(blank=True, null=True)
    total_occupied = models.IntegerField(blank=True, null=True)
    regular_vacant = models.IntegerField(blank=True, null=True)
    pha_total_units = models.IntegerField(blank=True, null=True)
    percent_occupied = models.TextField(blank=True, null=True)
    people_per_unit = models.FloatField(blank=True, null=True)
    people_total = models.IntegerField(blank=True, null=True)
    rent_per_month = models.IntegerField(blank=True, null=True)
    median_inc_amnt = models.IntegerField(blank=True, null=True)
    hh_income = models.IntegerField(blank=True, null=True)
    person_income = models.IntegerField(blank=True, null=True)
    pct_lt5k = models.FloatField(blank=True, null=True)
    pct_5k_lt10k = models.FloatField(blank=True, null=True)
    pct_10k_lt15k = models.FloatField(blank=True, null=True)
    pct_15k_lt20k = models.FloatField(blank=True, null=True)
    pct_ge20k = models.FloatField(blank=True, null=True)
    pct_lt80_median = models.TextField(blank=True, null=True)
    pct_lt50_median = models.FloatField(blank=True, null=True)
    pct_lt30_median = models.FloatField(blank=True, null=True)
    pct_bed1 = models.FloatField(blank=True, null=True)
    pct_bed2 = models.FloatField(blank=True, null=True)
    pct_bed3 = models.FloatField(blank=True, null=True)
    pct_overhoused = models.FloatField(blank=True, null=True)
    tminority = models.TextField(blank=True, null=True)
    tpoverty = models.TextField(blank=True, null=True)
    tpct_ownsfd = models.TextField(blank=True, null=True)
    chldrn_mbr_cnt = models.IntegerField(blank=True, null=True)
    eldly_prcnt = models.TextField(blank=True, null=True)
    pct_disabled_lt62_all = models.TextField(blank=True, null=True)
    scattered_site_ind = models.TextField(blank=True, null=True)
    pd_status_type_code = models.TextField(blank=True, null=True)
    geom = models.PointField(db_column='_geom', blank=True, null=True)
    geom_webmercator = models.PointField(db_column='_the_geom_webmercator', srid=3857, blank=True, null=True)

    hc_index_fields = ('development_code',)

    class Meta:
        managed = False
        db_table = '7cc60ad7-b209-46f2-bdda-9755d8a42461'


class HUDPublicHousingBuildings(HousingDataset):
    development_code = models.TextField(blank=True, null=True)

    full_text = models.TextField(db_column='_full_text', blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    geocoding_accuracy = models.TextField(blank=True, null=True)
    county_fips_code = models.TextField(blank=True, null=True)
    census_tract = models.TextField(blank=True, null=True)
    municipality_fips = models.TextField(blank=True, null=True)
    municipality_name = models.TextField(blank=True, null=True)
    hud_property_name = models.TextField(blank=True, null=True)
    property_street_address = models.TextField(blank=True, null=True)
    city = models.TextField(blank=True, null=True)
    state = models.TextField(blank=True, null=True)
    zip_code = models.TextField(blank=True, null=True)
    units = models.IntegerField(blank=True, null=True)
    owner_organization_name = models.TextField(blank=True, null=True)
    participant_code = models.TextField(blank=True, null=True)
    formal_participant_name = models.TextField(blank=True, null=True)
    project_name = models.TextField(blank=True, null=True)
    total_dwelling_units = models.IntegerField(blank=True, null=True)
    acc_units = models.IntegerField(blank=True, null=True)
    total_occupied = models.IntegerField(blank=True, null=True)
    regular_vacant = models.IntegerField(blank=True, null=True)
    pha_total_units = models.IntegerField(blank=True, null=True)
    percent_occupied = models.TextField(blank=True, null=True)
    people_per_unit = models.FloatField(blank=True, null=True)
    people_total = models.IntegerField(blank=True, null=True)
    rent_per_month = models.IntegerField(blank=True, null=True)
    median_inc_amnt = models.IntegerField(blank=True, null=True)
    hh_income = models.IntegerField(blank=True, null=True)
    person_income = models.IntegerField(blank=True, null=True)
    pct_lt5k = models.FloatField(blank=True, null=True)
    pct_5k_lt10k = models.FloatField(blank=True, null=True)
    pct_10k_lt15k = models.FloatField(blank=True, null=True)
    pct_15k_lt20k = models.FloatField(blank=True, null=True)
    pct_ge20k = models.FloatField(blank=True, null=True)
    pct_lt80_median = models.TextField(blank=True, null=True)
    pct_lt50_median = models.FloatField(blank=True, null=True)
    pct_lt30_median = models.FloatField(blank=True, null=True)
    pct_bed1 = models.FloatField(blank=True, null=True)
    pct_bed2 = models.FloatField(blank=True, null=True)
    pct_bed3 = models.FloatField(blank=True, null=True)
    pct_overhoused = models.FloatField(blank=True, null=True)
    tminority = models.TextField(blank=True, null=True)
    tpoverty = models.TextField(blank=True, null=True)
    tpct_ownsfd = models.TextField(blank=True, null=True)
    chldrn_mbr_cnt = models.IntegerField(blank=True, null=True)
    eldly_prcnt = models.TextField(blank=True, null=True)
    pct_disabled_lt62_all = models.TextField(blank=True, null=True)
    national_building_id = models.TextField(blank=True, null=True)
    geom = models.PointField(db_column='_geom', blank=True, null=True)
    geom_webmercator = models.PointField(db_column='_the_geom_webmercator', srid=3857, blank=True, null=True)

    hc_index_fields = ('development_code',)

    class Meta:
        managed = False
        db_table = '6269354d-bac6-4c2e-ad07-2dd7e2ab252e'


class SubsidyExtractFromHUDInsuredMultifamilyProperties(HousingDataset):
    property_id = models.TextField(blank=True, null=True)

    full_text = models.TextField(db_column='_full_text', blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    geocoding_accuracy = models.TextField(blank=True, null=True)
    county = models.TextField(blank=True, null=True)
    county_fips_code = models.TextField(blank=True, null=True)
    congressional_district_code = models.TextField(blank=True, null=True)
    census_tract = models.TextField(blank=True, null=True)
    municipality_fips = models.TextField(blank=True, null=True)
    municipality_name = models.TextField(blank=True, null=True)
    hud_property_name = models.TextField(blank=True, null=True)
    property_street_address = models.TextField(blank=True, null=True)
    city = models.TextField(blank=True, null=True)
    state = models.TextField(blank=True, null=True)
    zip_code = models.TextField(blank=True, null=True)
    units = models.IntegerField(blank=True, null=True)
    assisted_units = models.IntegerField(blank=True, null=True)
    occupancy_date = models.DateField(blank=True, null=True)
    property_category_name = models.TextField(blank=True, null=True)
    property_manager_name = models.TextField(blank=True, null=True)
    property_manager_company = models.TextField(blank=True, null=True)
    property_manager_address = models.TextField(blank=True, null=True)
    property_manager_phone = models.TextField(blank=True, null=True)
    property_manager_email = models.TextField(blank=True, null=True)
    contract_id = models.TextField(blank=True, null=True)
    program_type = models.TextField(blank=True, null=True)
    subsidy_units = models.IntegerField(blank=True, null=True)
    subsidy_expiration_date = models.DateField(blank=True, null=True)
    count_0br = models.IntegerField(blank=True, null=True)
    count_1br = models.IntegerField(blank=True, null=True)
    count_2br = models.IntegerField(blank=True, null=True)
    count_3br = models.IntegerField(blank=True, null=True)
    count_4br = models.IntegerField(blank=True, null=True)
    count_5plusbr = models.IntegerField(blank=True, null=True)
    servicing_site_name_loan = models.TextField(blank=True, null=True)
    inspection_id = models.IntegerField(blank=True, null=True)
    inspection_score = models.TextField(blank=True, null=True)
    client_group_name = models.TextField(blank=True, null=True)
    client_group_type = models.TextField(blank=True, null=True)
    geom = models.PointField(db_column='_geom', blank=True, null=True)
    geom_webmercator = models.PointField(db_column='_the_geom_webmercator', srid=3857, blank=True, null=True)

    hc_index_fields = ('property_id',)

    class Meta:
        managed = False
        db_table = '7eeabaa5-bd27-4df0-9459-d56acd826451'
        ordering = ['-subsidy_expiration_date']


class SubsidyExtractFromMultifamilyAssistanceAndSection8Contracts(HousingDataset):
    property_id = models.TextField(blank=True, null=True)

    full_text = models.TextField(db_column='_full_text', blank=True, null=True)
    county_fips_code = models.TextField(blank=True, null=True)
    county = models.TextField(blank=True, null=True)
    congressional_district_code = models.TextField(blank=True, null=True)
    municipality_name = models.TextField(blank=True, null=True)
    hud_property_name = models.TextField(blank=True, null=True)
    property_street_address = models.TextField(blank=True, null=True)
    city = models.TextField(blank=True, null=True)
    state = models.TextField(blank=True, null=True)
    zip_code = models.IntegerField(blank=True, null=True)
    units = models.IntegerField(blank=True, null=True)
    property_category_name = models.TextField(blank=True, null=True)
    owner_organization_name = models.TextField(blank=True, null=True)
    owner_address = models.TextField(blank=True, null=True)
    owner_phone = models.TextField(blank=True, null=True)
    owner_type = models.TextField(blank=True, null=True)
    owner_effective_date = models.DateField(blank=True, null=True)
    owner_id = models.IntegerField(blank=True, null=True)
    property_manager_name = models.TextField(blank=True, null=True)
    property_manager_company = models.TextField(blank=True, null=True)
    property_manager_address = models.TextField(blank=True, null=True)
    property_manager_phone = models.TextField(blank=True, null=True)
    property_manager_email = models.TextField(blank=True, null=True)
    property_manager_type = models.TextField(blank=True, null=True)
    servicing_site_name = models.TextField(blank=True, null=True)
    geom = models.PointField(db_column='_geom', blank=True, null=True)
    geom_webmercator = models.PointField(db_column='_the_geom_webmercator', srid=3857, blank=True, null=True)

    hc_index_fields = ('property_id',)

    class Meta:
        managed = False
        db_table = '127d12cd-9718-4b44-9cc1-2673a1a50dba'
        ordering = ['-owner_effective_date']


class MultifamilyAssistanceAndSection8Contracts(HousingDataset):
    property_id = models.TextField(blank=True, null=True)

    full_text = models.TextField(db_column='_full_text', blank=True, null=True)
    hud_property_name = models.TextField(blank=True, null=True)
    assisted_units = models.IntegerField(blank=True, null=True)
    count_0br = models.IntegerField(blank=True, null=True)
    count_1br = models.IntegerField(blank=True, null=True)
    count_2br = models.IntegerField(blank=True, null=True)
    count_3br = models.IntegerField(blank=True, null=True)
    count_4br = models.IntegerField(blank=True, null=True)
    count_5plusbr = models.IntegerField(blank=True, null=True)
    contract_id = models.TextField(blank=True, null=True)
    program_type = models.TextField(blank=True, null=True)
    subsidy_start_date = models.DateField(blank=True, null=True)
    subsidy_expiration_date = models.TextField(blank=True, null=True)
    contract_duration_months = models.IntegerField(blank=True, null=True)

    geom = models.PointField(db_column='_geom', blank=True, null=True)
    geom_webmercator = models.PointField(db_column='_the_geom_webmercator', srid=3857, blank=True, null=True)

    hc_index_fields = ('property_id',)

    class Meta:
        managed = False
        db_table = '438a732d-c86f-4a06-bff8-61eb6ebe7328'
        ordering = ['-subsidy_expiration_date']


class HUDInsuredMultifamilyProperties(HousingDataset):
    property_id = models.TextField(blank=True, null=True)
    fha_loan_id = models.TextField(blank=True, null=True)

    full_text = models.TextField(db_column='_full_text', blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    geocoding_accuracy = models.TextField(blank=True, null=True)
    county = models.TextField(blank=True, null=True)
    county_fips_code = models.TextField(blank=True, null=True)
    congressional_district_code = models.TextField(blank=True, null=True)
    census_tract = models.TextField(blank=True, null=True)
    municipality_fips = models.TextField(blank=True, null=True)
    municipality_name = models.TextField(blank=True, null=True)
    hud_property_name = models.TextField(blank=True, null=True)
    property_street_address = models.TextField(blank=True, null=True)
    city = models.TextField(blank=True, null=True)
    state = models.TextField(blank=True, null=True)
    zip_code = models.TextField(blank=True, null=True)
    units = models.IntegerField(blank=True, null=True)
    assisted_units = models.IntegerField(blank=True, null=True)
    property_category_name = models.TextField(blank=True, null=True)
    property_manager_name = models.TextField(blank=True, null=True)
    property_manager_phone = models.TextField(blank=True, null=True)
    associated_fha_loan_id = models.TextField(blank=True, null=True)
    initial_endorsement_date = models.DateField(blank=True, null=True)
    original_mortgage_amount = models.IntegerField(blank=True, null=True)
    maturity_date = models.DateField(blank=True, null=True)
    program_category = models.TextField(blank=True, null=True)
    program_category_2 = models.TextField(blank=True, null=True)
    loan_units = models.IntegerField(blank=True, null=True)
    client_group_name = models.TextField(blank=True, null=True)
    client_group_type = models.TextField(blank=True, null=True)
    section_of_act_code = models.TextField(blank=True, null=True)
    servicing_site_name_loan = models.TextField(blank=True, null=True)
    geom = models.PointField(db_column='_geom', blank=True, null=True)
    geom_webmercator = models.PointField(db_column='_the_geom_webmercator', srid=3857, blank=True, null=True)

    hc_index_fields = ('property_id', 'fha_loan_id',)

    class Meta:
        managed = False
        db_table = 'c099b5b9-df5d-4380-9cb3-6c45b03ac8b4'
        ordering = ['-initial_endorsement_date']


class HUDMultifamilyInspectionScores(HousingDataset):
    property_id = models.TextField(blank=True, null=True)

    full_text = models.TextField(db_column='_full_text', blank=True, null=True)
    hud_property_name = models.TextField(blank=True, null=True)
    inspection_property_id_multiformat = models.TextField(blank=True, null=True)
    city = models.TextField(blank=True, null=True)
    state = models.TextField(blank=True, null=True)
    inspection_id = models.TextField(blank=True, null=True)
    inspection_score = models.TextField(blank=True, null=True)
    inspection_date = models.DateField(blank=True, null=True)
    geom = models.PointField(db_column='_geom', blank=True, null=True)
    geom_webmercator = models.PointField(db_column='_the_geom_webmercator', srid=3857, blank=True, null=True)

    hc_index_fields = ('property_id',)

    class Meta:
        managed = False
        db_table = '7d4ad5ee-7229-4aa6-b3a2-69779fe5c52a'
        ordering = ['-inspection_date']


class LIHTCDataFromPHFA(HousingDataset):
    pmindx = models.TextField(blank=True, null=True)

    full_text = models.TextField(db_column='_full_text', blank=True, null=True)
    hud_property_name = models.TextField(blank=True, null=True)
    assisted_units = models.IntegerField(blank=True, null=True)
    total_lihtc_allocation = models.IntegerField(blank=True, null=True)
    unit_restriction = models.TextField(blank=True, null=True)
    lihtc_credit = models.TextField(blank=True, null=True)
    lihtc_year_allocated = models.IntegerField(blank=True, null=True)
    lihtc_year_in_service = models.IntegerField(blank=True, null=True)
    last_year_of_rca = models.IntegerField(blank=True, null=True)
    geom = models.PointField(db_column='_geom', blank=True, null=True)
    geom_webmercator = models.PointField(db_column='_the_geom_webmercator', srid=3857, blank=True, null=True)

    hc_index_fields = ('pmindx',)

    class Meta:
        managed = False
        db_table = 'f6a77bc1-e3c1-403a-86bc-40b906124af6'


class DemographicsByHousingProjectFromPHFA(HousingDataset):
    property_id = models.TextField(blank=True, null=True)
    pmindx = models.TextField(blank=True, null=True)
    normalized_state_id = models.TextField(blank=True, null=True)
    fha_loan_id = models.TextField(blank=True, null=True)

    full_text = models.TextField(db_column='_full_text', blank=True, null=True)
    application_number = models.TextField(blank=True, null=True)
    state_id = models.TextField(blank=True, null=True)
    contract_id = models.TextField(blank=True, null=True)
    hud_property_name = models.TextField(blank=True, null=True)
    property_street_address = models.TextField(blank=True, null=True)
    city = models.TextField(blank=True, null=True)
    state = models.TextField(blank=True, null=True)
    zip_code = models.TextField(blank=True, null=True)
    owner_organization_name = models.TextField(blank=True, null=True)
    assisted_units = models.IntegerField(blank=True, null=True)
    demographic = models.TextField(blank=True, null=True)
    physical_disability_housing = models.BooleanField(blank=True, null=True)
    mental_disability_housing = models.BooleanField(blank=True, null=True)
    homeless_housing = models.BooleanField(blank=True, null=True)
    owner_representative = models.TextField(blank=True, null=True)
    property_manager_company = models.TextField(blank=True, null=True)
    scattered_sites = models.BooleanField(blank=True, null=True)
    geom = models.PointField(db_column='_geom', blank=True, null=True)
    geom_webmercator = models.PointField(db_column='_the_geom_webmercator', srid=3857, blank=True, null=True)

    hc_index_fields = ('property_id', 'pmindx', 'normalized_state_id', 'fha_loan_id',)

    class Meta:
        managed = False
        db_table = 'fcb7cd5d-71f6-4f38-bb78-a3002be47ed6'


class PHFAStats(HousingDataset):
    pmindx = models.IntegerField(blank=True, null=True)

    full_text = models.TextField(db_column='_full_text', blank=True, null=True)
    hud_property_name = models.TextField(blank=True, null=True)
    total_units = models.IntegerField(blank=True, null=True)
    count_0br = models.IntegerField(blank=True, null=True)
    count_1br = models.IntegerField(blank=True, null=True)
    count_2br = models.IntegerField(blank=True, null=True)
    count_3br = models.IntegerField(blank=True, null=True)
    count_4br = models.IntegerField(blank=True, null=True)
    count_5br = models.IntegerField(blank=True, null=True)
    count_6br = models.IntegerField(blank=True, null=True)
    plus_1_manager_unit = models.IntegerField(blank=True, null=True)
    number_20percent_ami_limit = models.IntegerField(db_column='20percent_ami_limit', blank=True, null=True)
    number_30percent_ami_limit = models.IntegerField(db_column='30percent_ami_limit', blank=True, null=True)
    number_40percent_ami_limit = models.IntegerField(db_column='40percent_ami_limit', blank=True, null=True)
    number_50percent_ami_limit = models.IntegerField(db_column='50percent_ami_limit', blank=True, null=True)
    number_60percent_ami_limit = models.IntegerField(db_column='60percent_ami_limit', blank=True, null=True)
    number_80percent_ami_limit = models.IntegerField(db_column='80percent_ami_limit', blank=True, null=True)
    market_rate = models.IntegerField(blank=True, null=True)
    other_income_limit = models.IntegerField(blank=True, null=True)
    uncategorized_income_limit = models.IntegerField(blank=True, null=True)
    units_w_section_811_subsidy = models.IntegerField(blank=True, null=True)
    units_w_section_8_fair_market_rent = models.IntegerField(blank=True, null=True)
    units_w_housing_vouchers = models.IntegerField(blank=True, null=True)
    units_w_staff_unit = models.IntegerField(blank=True, null=True)
    units_w_other_subsidy_type = models.IntegerField(blank=True, null=True)
    units_w_project_based_section_8_certificate = models.IntegerField(blank=True, null=True)
    units_w_uncategorized_subsidy = models.IntegerField(blank=True, null=True)
    geom = models.PointField(db_column='_geom', blank=True, null=True)
    geom_webmercator = models.PointField(db_column='_the_geom_webmercator', srid=3857, blank=True, null=True)

    hc_index_fields = ('pmindx',)

    class Meta:
        managed = False
        db_table = 'a6b93b7b-e04e-42c9-96f9-ee788e4f0978'
