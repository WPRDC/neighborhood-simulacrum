from rest_framework import serializers
from rest_framework_gis.fields import GeometrySerializerMethodField
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from public_housing.housing_datasets import PHFAStats, ActiveHUDMultifamilyInsuredMortgages, \
    HUDMultifamilyFiscalYearProduction, LIHTC, AllBuildingsFromLIHTCProjects, HUDInspectionScores, \
    HUDPublicHousingDevelopments, HUDPublicHousingBuildings, SubsidyExtractFromHUDInsuredMultifamilyProperties, \
    SubsidyExtractFromMultifamilyAssistanceAndSection8Contracts, MultifamilyAssistanceAndSection8Contracts, \
    HUDInsuredMultifamilyProperties, HUDMultifamilyInspectionScores, LIHTCDataFromPHFA, \
    DemographicsByHousingProjectFromPHFA, HouseCatSubsidyListing
from public_housing.models import ProjectIndex, Watchlist


class ActiveHUDMultifamilyInsuredMortgagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActiveHUDMultifamilyInsuredMortgages
        fields = (
            'fha_loan_id',
            'hud_property_name',
            'property_street_address',
            'city',
            'state',
            'zip_code',
            'units',
            'initial_endorsement_date',
            'original_mortgage_amount',
            'maturity_date',
            'term_in_months',
            'interest_rate',
            'current_principal_and_interest',
            'amoritized_principal_balance',
            'holder_name',
            'holder_city',
            'holder_state',
            'servicer_name',
            'servicer_city',
            'servicer_state',
            'section_of_act_code',
            'program_category',
        )


class HUDMultifamilyFiscalYearProductionSerializer(serializers.ModelSerializer):
    class Meta:
        model = HUDMultifamilyFiscalYearProduction
        fields = (
            'fha_loan_id',
            'hud_property_name',
            'city',
            'state',
            'initial_endorsement_date',
            'original_mortgage_amount',
            'program_category',
            'units',
            'basic_fha_risk_share_or_other',
            'current_status_of_loan',
            'date_of_firm_issue',
            'firm_commitment_lender',
            'holder_name',
        )


class LIHTCSerializer(serializers.ModelSerializer):
    class Meta:
        model = LIHTC
        fields = (
            'lihtc_project_id',
            'normalized_state_id',
            'census_tract',
            'census_tract_2000',
            'county_fips_code',
            'municipality_fips',
            'hud_property_name',
            'property_street_address',
            'city',
            'state',
            'zip_code',
            'units',
            'assisted_units',
            'count_0br',
            'count_1br',
            'count_2br',
            'count_3br',
            'count_4br',
            'federal_id',
            'state_id',
            'lihtc_credit',
            'lihtc_construction_type',
            'lihtc_year_allocated',
            'lihtc_year_in_service',
            'lihtc_amount',
            'fmha_514_loan',
            'fmha_515_loan',
            'fmha_538_loan',
            'scattered_site_ind',

        )


class AllBuildingsFromLIHTCProjectsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AllBuildingsFromLIHTCProjects
        fields = (
            'lihtc_project_id',
            'normalized_state_id',
            'hud_property_name',
            'property_street_address',
            'city',
            'state',
            'zip_code',
            'state_id',
        )


class HUDInspectionScoresSerializer(serializers.ModelSerializer):
    class Meta:
        model = HUDInspectionScores
        fields = (
            'development_code',
            'state',
            'county',
            'county_fips_code',
            'hud_property_name',
            'property_street_address',
            'inspection_id',
            'inspection_property_id_multiformat',
            'inspection_score',
            'inspection_date',
            'participant_code',
            'formal_participant_name',
        )


class HUDPublicHousingDevelopmentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = HUDPublicHousingDevelopments
        fields = (
            'development_code',
            'geocoding_accuracy',
            'county_fips_code',
            'census_tract',
            'municipality_fips',
            'municipality_name',
            'hud_property_name',
            'property_street_address',
            'city',
            'state',
            'zip_code',
            'units',
            'owner_organization_name',
            'participant_code',
            'formal_participant_name',
            'project_name',
            'total_dwelling_units',
            'acc_units',
            'total_occupied',
            'regular_vacant',
            'pha_total_units',
            'percent_occupied',
            'people_per_unit',
            'people_total',
            'rent_per_month',
            'median_inc_amnt',
            'hh_income',
            'person_income',
            'pct_lt5k',
            'pct_5k_lt10k',
            'pct_10k_lt15k',
            'pct_15k_lt20k',
            'pct_ge20k',
            'pct_lt80_median',
            'pct_lt50_median',
            'pct_lt30_median',
            'pct_bed1',
            'pct_bed2',
            'pct_bed3',
            'pct_overhoused',
            'tminority',
            'tpoverty',
            'tpct_ownsfd',
            'chldrn_mbr_cnt',
            'eldly_prcnt',
            'pct_disabled_lt62_all',
            'scattered_site_ind',
            'pd_status_type_code',
        )


class HUDPublicHousingBuildingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = HUDPublicHousingBuildings
        fields = (
            'development_code',
            'geocoding_accuracy',
            'county_fips_code',
            'census_tract',
            'municipality_fips',
            'municipality_name',
            'hud_property_name',
            'property_street_address',
            'city',
            'state',
            'zip_code',
            'units',
            'owner_organization_name',
            'participant_code',
            'formal_participant_name',
            'project_name',
            'total_dwelling_units',
            'acc_units',
            'total_occupied',
            'regular_vacant',
            'pha_total_units',
            'percent_occupied',
            'people_per_unit',
            'people_total',
            'rent_per_month',
            'median_inc_amnt',
            'hh_income',
            'person_income',
            'pct_lt5k',
            'pct_5k_lt10k',
            'pct_10k_lt15k',
            'pct_15k_lt20k',
            'pct_ge20k',
            'pct_lt80_median',
            'pct_lt50_median',
            'pct_lt30_median',
            'pct_bed1',
            'pct_bed2',
            'pct_bed3',
            'pct_overhoused',
            'tminority',
            'tpoverty',
            'tpct_ownsfd',
            'chldrn_mbr_cnt',
            'eldly_prcnt',
            'pct_disabled_lt62_all',
            'national_building_id',
        )


class SubsidyExtractFromHUDInsuredMultifamilyPropertiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubsidyExtractFromHUDInsuredMultifamilyProperties
        fields = (
            'property_id',
            'geocoding_accuracy',
            'county',
            'county_fips_code',
            'congressional_district_code',
            'census_tract',
            'municipality_fips',
            'municipality_name',
            'hud_property_name',
            'property_street_address',
            'city',
            'state',
            'zip_code',
            'units',
            'assisted_units',
            'occupancy_date',
            'property_category_name',
            'property_manager_name',
            'property_manager_company',
            'property_manager_address',
            'property_manager_phone',
            'property_manager_email',
            'contract_id',
            'program_type',
            'subsidy_units',
            'subsidy_expiration_date',
            'count_0br',
            'count_1br',
            'count_2br',
            'count_3br',
            'count_4br',
            'count_5plusbr',
            'servicing_site_name_loan',
            'inspection_id',
            'inspection_score',
            'client_group_name',
            'client_group_type',
        )


class SubsidyExtractFromMultifamilyAssistanceAndSection8ContractsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubsidyExtractFromMultifamilyAssistanceAndSection8Contracts
        fields = (
            'property_id',
            'county_fips_code',
            'county',
            'congressional_district_code',
            'municipality_name',
            'hud_property_name',
            'property_street_address',
            'city',
            'state',
            'zip_code',
            'units',
            'property_category_name',
            'owner_organization_name',
            'owner_address',
            'owner_phone',
            'owner_type',
            'owner_effective_date',
            'owner_id',
            'property_manager_name',
            'property_manager_company',
            'property_manager_address',
            'property_manager_phone',
            'property_manager_email',
            'property_manager_type',
            'servicing_site_name',

        )


class MultifamilyAssistanceAndSection8ContractsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MultifamilyAssistanceAndSection8Contracts
        fields = (
            'property_id',
            'hud_property_name',
            'assisted_units',
            'count_0br',
            'count_1br',
            'count_2br',
            'count_3br',
            'count_4br',
            'count_5plusbr',
            'contract_id',
            'program_type',
            'subsidy_start_date',
            'subsidy_expiration_date',
            'contract_duration_months',
        )


class HUDInsuredMultifamilyPropertiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = HUDInsuredMultifamilyProperties
        fields = (
            'property_id',
            'fha_loan_id',
            'geocoding_accuracy',
            'county',
            'county_fips_code',
            'congressional_district_code',
            'census_tract',
            'municipality_fips',
            'municipality_name',
            'hud_property_name',
            'property_street_address',
            'city',
            'state',
            'zip_code',
            'units',
            'assisted_units',
            'property_category_name',
            'property_manager_name',
            'property_manager_phone',
            'associated_fha_loan_id',
            'initial_endorsement_date',
            'original_mortgage_amount',
            'maturity_date',
            'program_category',
            'program_category_2',
            'loan_units',
            'client_group_name',
            'client_group_type',
            'section_of_act_code',
            'servicing_site_name_loan',
        )


class HUDMultifamilyInspectionScoresSerializer(serializers.ModelSerializer):
    class Meta:
        model = HUDMultifamilyInspectionScores
        fields = (
            'property_id',
            'hud_property_name',
            'inspection_property_id_multiformat',
            'city',
            'state',
            'inspection_id',
            'inspection_score',
            'inspection_date',
        )


class LIHTCDataFromPHFASerializer(serializers.ModelSerializer):
    class Meta:
        model = LIHTCDataFromPHFA
        fields = (
            'pmindx',
            'hud_property_name',
            'assisted_units',
            'total_lihtc_allocation',
            'unit_restriction',
            'lihtc_credit',
            'lihtc_year_allocated',
            'lihtc_year_in_service',
            'last_year_of_rca',
        )


class DemographicsByHousingProjectFromPHFASerializer(serializers.ModelSerializer):
    class Meta:
        model = DemographicsByHousingProjectFromPHFA
        fields = (
            'property_id',
            'pmindx',
            'normalized_state_id',
            'fha_loan_id',
            'application_number',
            'state_id',
            'contract_id',
            'hud_property_name',
            'property_street_address',
            'city',
            'state',
            'zip_code',
            'owner_organization_name',
            'assisted_units',
            'demographic',
            'physical_disability_housing',
            'mental_disability_housing',
            'homeless_housing',
            'owner_representative',
            'property_manager_company',
            'scattered_sites',
        )


class PHFAStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PHFAStats
        fields = (
            'pmindx',
            'hud_property_name',
            'total_units',
            'count_0br',
            'count_1br',
            'count_2br',
            'count_3br',
            'count_4br',
            'count_5br',
            'count_6br',
            'plus_1_manager_unit',
            'number_20percent_ami_limit',
            'number_30percent_ami_limit',
            'number_40percent_ami_limit',
            'number_50percent_ami_limit',
            'number_60percent_ami_limit',
            'number_80percent_ami_limit',
            'market_rate',
            'other_income_limit',
            'uncategorized_income_limit',
            'units_w_section_811_subsidy',
            'units_w_section_8_fair_market_rent',
            'units_w_housing_vouchers',
            'units_w_staff_unit',
            'units_w_other_subsidy_type',
            'units_w_project_based_section_8_certificate',
            'units_w_uncategorized_subsidy',
        )


class HouseCatSubsidyListingSerializer(serializers.ModelSerializer):
    class Meta:
        model = HouseCatSubsidyListing
        fields = (
            'subsidy_data_source',
            'subsidy_expiration_date',
        )


###################
# Project Index

class ProjectIndexSerializer(serializers.ModelSerializer):
    active_hud_multifamily_insured_mortgages = ActiveHUDMultifamilyInsuredMortgagesSerializer(many=True)
    hud_multifamily_fiscal_year_production = HUDMultifamilyFiscalYearProductionSerializer(many=True)
    lihtc = LIHTCSerializer(many=True)
    all_buildings_from_lihtc_projects = AllBuildingsFromLIHTCProjectsSerializer(many=True)
    hud_inspection_scores = HUDInspectionScoresSerializer(many=True)
    hud_public_housing_developments = HUDPublicHousingDevelopmentsSerializer(many=True)
    hud_public_housing_buildings = HUDPublicHousingBuildingsSerializer(many=True)
    subsidy_extract_hud_insured_multifamily_properties = \
        SubsidyExtractFromHUDInsuredMultifamilyPropertiesSerializer(many=True)
    subsidy_extract_multifamily_assistance_and_section8_contracts = \
        SubsidyExtractFromMultifamilyAssistanceAndSection8ContractsSerializer(many=True)
    multifamily_assistance_and_section_8_contracts = MultifamilyAssistanceAndSection8ContractsSerializer(many=True)
    hud_insured_multifamily_properties = HUDInsuredMultifamilyPropertiesSerializer(many=True)
    hud_multifamily_inspection_scores = HUDMultifamilyInspectionScoresSerializer(many=True)
    lihtc_data_from_phfa = LIHTCDataFromPHFASerializer(many=True)
    demographics_by_housing_project_from_phfa = DemographicsByHousingProjectFromPHFASerializer(many=True)
    phfa_stats = PHFAStatsSerializer(many=True)
    subsidy_info = HouseCatSubsidyListingSerializer(many=True)

    class Meta:
        model = ProjectIndex
        fields = (
            'id',
            'slug',
            'name',
            'description',
            'property_id',
            'hud_property_name',
            'property_street_address',
            'municipality_name',
            'city',
            'zip_code',
            'units',
            'scattered_sites',
            'census_tract',
            'crowdsourced_id',
            'house_cat_id',
            'status',

            # Connected dataset properties
            'active_hud_multifamily_insured_mortgages',
            'hud_multifamily_fiscal_year_production',
            'lihtc',
            'all_buildings_from_lihtc_projects',
            'hud_inspection_scores',
            'hud_public_housing_developments',
            'hud_public_housing_buildings',
            'subsidy_extract_hud_insured_multifamily_properties',
            'subsidy_extract_multifamily_assistance_and_section8_contracts',
            'multifamily_assistance_and_section_8_contracts',
            'hud_insured_multifamily_properties',
            'hud_multifamily_inspection_scores',
            'lihtc_data_from_phfa',
            'demographics_by_housing_project_from_phfa',
            'phfa_stats',
            'subsidy_info',
        )


class ProjectIndexBriefSerializer(serializers.HyperlinkedModelSerializer):
    centroid = serializers.SerializerMethodField()

    class Meta:
        model = ProjectIndex
        fields = (
            'url',
            'id',
            'slug',
            'name',
            'description',
            'property_id',
            'hud_property_name',
            'property_street_address',
            'municipality_name',
            'city',
            'zip_code',
            'units',
            'scattered_sites',
            'census_tract',
            'crowdsourced_id',
            'house_cat_id',
            'status',
            'centroid'
        )

    def get_centroid(self, obj):
        try:
            return obj.centroid.coords
        except:
            return None


class ProjectIndexGeoJSONSerializer(GeoFeatureModelSerializer):
    the_geom = GeometrySerializerMethodField()

    def get_the_geom(self, obj: ProjectIndex):
        return obj.the_geom

    class Meta:
        model = ProjectIndex
        geo_field = 'the_geom'
        fields = (
            'url',
            'id',
            'property_id',
            'hud_property_name',
            'property_street_address',
            'municipality_name',
            'city',
            'zip_code',
            'units',
            'scattered_sites',
            'census_tract',
            'crowdsourced_id',
            'house_cat_id',
            'status',
        )


class WatchlistDetailedSerializer(serializers.ModelSerializer):
    project_indices = ProjectIndexBriefSerializer(many=True)

    class Meta:
        model = Watchlist
        fields = (
            'id',
            'slug',
            'user_name',
            'project_indices'
        )


class WatchlistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Watchlist
        fields = (
            'id',
            'slug',
            'user_name',
            'items',
        )
