from datetime import datetime
from functools import lru_cache
from typing import Type

from django.contrib.gis.db import models
from django.contrib.gis.geos import Point, MultiPoint
from django.db.models import QuerySet

from profiles.abstract_models import DatastoreDataset
from public_housing.housing_datasets import (
    ActiveHUDMultifamilyInsuredMortgages,
    HUDInspectionScores,
    SubsidyExtractFromHUDInsuredMultifamilyProperties,
    SubsidyExtractFromMultifamilyAssistanceAndSection8Contracts,
    HUDInsuredMultifamilyProperties,
    HUDMultifamilyInspectionScores,
    MultifamilyAssistanceAndSection8Contracts,
    HUDMultifamilyFiscalYearProduction,
    DemographicsByHousingProjectFromPHFA,
    HUDPublicHousingDevelopments,
    AllBuildingsFromLIHTCProjects,
    HUDPublicHousingBuildings,
    LIHTCDataFromPHFA,
    PHFAStats,
    LIHTC,
    HousingDataset, ContractID, DevelopmentCode, FHALoanID, LIHTCProjectID, NormalizeStateID, PMIndx, LookupTable,
    HouseCatSubsidyListing,
)

DATASETS: list[Type[HousingDataset]] = [
    ActiveHUDMultifamilyInsuredMortgages,
    HUDInspectionScores,
    SubsidyExtractFromHUDInsuredMultifamilyProperties,
    SubsidyExtractFromMultifamilyAssistanceAndSection8Contracts,
    HUDInsuredMultifamilyProperties,
    HUDMultifamilyInspectionScores,
    MultifamilyAssistanceAndSection8Contracts,
    HUDMultifamilyFiscalYearProduction,
    DemographicsByHousingProjectFromPHFA,
    HUDPublicHousingDevelopments,
    AllBuildingsFromLIHTCProjects,
    HUDPublicHousingBuildings,
    LIHTCDataFromPHFA,
    PHFAStats,
    LIHTC,
]


def get_fkeys(model: Type['LookupTable'], origin_id: int):
    """ returns a list of matching foreign keys to the model from project index with origin_id"""
    qs = model.objects.filter(projectindex_id=origin_id).values('projectidentifier_id')
    return [item['projectidentifier_id'] for item in qs]


class ProjectIndex(DatastoreDataset):
    id = models.IntegerField(unique=True, primary_key=True)

    property_id = models.TextField(blank=True, null=True)
    hud_property_name = models.TextField(blank=True, null=True)
    property_street_address = models.TextField(blank=True, null=True)
    municipality_name = models.TextField(blank=True, null=True)
    city = models.TextField(blank=True, null=True)
    zip_code = models.TextField(blank=True, null=True)
    units = models.TextField(blank=True, null=True)
    scattered_sites = models.CharField(max_length=20, blank=True, null=True)
    latitude = models.TextField(blank=True, null=True)
    longitude = models.TextField(blank=True, null=True)
    census_tract = models.TextField(blank=True, null=True)
    crowdsourced_id = models.TextField(blank=True, null=True)
    house_cat_id = models.TextField(blank=True, null=True)

    status = models.TextField(blank=True, null=True)

    geom = models.MultiPointField(db_column='_geom', blank=True, null=True)
    geom_webmercator = models.MultiPointField(db_column='_the_geom_webmercator', srid=3857, blank=True, null=True)

    class Meta:
        managed = False
        db_table = '1885161c-65f3-4cb2-98aa-4402487ae888'

    @staticmethod
    @lru_cache
    def filter_by_subsidy_expiration(queryset: QuerySet['ProjectIndex'], date: str, method='lte') -> QuerySet[
        'ProjectIndex']:
        """ Finds subsidy listings that expire on or before `date` and returns ProjectIndexes that match """
        matching_ids = [subsidy.property_id for subsidy
                        in HouseCatSubsidyListing.objects.filter(subsidy_expiration_date__lte=date)
                        if subsidy.subsidy_expiration_date is not None]
        return queryset.filter(property_id__in=matching_ids)

    def get_data_for_std_field(self, std_field: str) -> list[dict]:
        """ Takes a standardized field name and searches for records containing it in the connected datasets """
        results = []
        for dataset in DATASETS:
            # call property that pulls related dataset data
            dataset_records = self.get_related_data(dataset)
            # if there are any records, search them for the field
            if dataset_records:
                for record in dataset_records:
                    results.append(getattr(record, std_field))
        return results

    def get_related_data(self, model: Type['HousingDataset']):
        """ Use metadata from the supplied model to find linked data to the instance index """
        index_fields = model.hc_index_fields
        # chain key array lookups by ORs
        query = {
            f'{index_field}__in': getattr(self, f'{index_field}_set')
            for index_field in index_fields
        }
        return model.objects.filter(**query)

    @property
    def slug(self):
        return str(self.id)

    @property
    def name(self):
        return f'{self.hud_property_name}'

    @property
    def description(self):
        return ''

    @property
    def the_geom(self):
        if self.geom:
            return self.geom
        if self.longitude and self.latitude:
            # todo: log when there are more than one lat or lng
            lngs = self.longitude.split('|')
            lats = self.latitude.split('|')
            return Point(float(lngs[0]), float(lats[0]))
        return None

    @property
    def all_foreign_keys(self):
        index_fields = ['fha_loan_id', 'lihtc_project_id', 'normalized_state_id', 'development_code', 'pmindx',
                        'property_id']
        return {
            f'{index_field}__in': getattr(self, f'{index_field}_set')
            for index_field in index_fields
        }

    @property
    def contract_id_set(self) -> list[str]:
        return get_fkeys(ContractID, self.id)

    @property
    def development_code_set(self) -> list[str]:
        return get_fkeys(DevelopmentCode, self.id)

    @property
    def fha_loan_id_set(self) -> list[str]:
        return get_fkeys(FHALoanID, self.id)

    @property
    def lihtc_project_id_set(self) -> list[str]:
        return get_fkeys(LIHTCProjectID, self.id)

    @property
    def normalized_state_id_set(self) -> list[str]:
        return get_fkeys(NormalizeStateID, self.id)

    @property
    def pmindx_set(self) -> list[str]:
        return get_fkeys(PMIndx, self.id)

    @property
    def property_id_set(self) -> list[str]:
        return [self.property_id]

    # Link each of the other datasets to this index
    # todo: for now, handle in python.
    #  once grokked, maybe better to move to DB layer or create models for `through` relations

    # -Active HUD Multifamily Insured Mortgages
    @property
    def active_hud_multifamily_insured_mortgages(self):
        return self.get_related_data(ActiveHUDMultifamilyInsuredMortgages)

    # -HUD Multifamily Fiscal Year Production
    @property
    def hud_multifamily_fiscal_year_production(self):
        return self.get_related_data(HUDMultifamilyFiscalYearProduction)

    # -LIHTC
    @property
    def lihtc(self):
        return self.get_related_data(LIHTC)

    # -All Buildings from LIHTC Projects
    @property
    def all_buildings_from_lihtc_projects(self):
        return self.get_related_data(AllBuildingsFromLIHTCProjects)

    # -HUD Inspection Scores
    @property
    def hud_inspection_scores(self):
        return self.get_related_data(HUDInspectionScores)

    # -HUD Public Housing Developments
    @property
    def hud_public_housing_developments(self):
        return self.get_related_data(HUDPublicHousingDevelopments)

    # -HUD Public Housing Buildings
    @property
    def hud_public_housing_buildings(self):
        return self.get_related_data(HUDPublicHousingBuildings)

    # -Subsidy extract from HUD Insured Multifamily Properties
    @property
    def subsidy_extract_hud_insured_multifamily_properties(self):
        return self.get_related_data(SubsidyExtractFromHUDInsuredMultifamilyProperties)

    # -Subsidy extract from Multifamily Assistance & Section 8 Contracts
    @property
    def subsidy_extract_multifamily_assistance_and_section8_contracts(self):
        return self.get_related_data(SubsidyExtractFromMultifamilyAssistanceAndSection8Contracts)

    # -Multifamily Assistance & Section 8 Contracts
    @property
    def multifamily_assistance_and_section_8_contracts(self):
        return self.get_related_data(MultifamilyAssistanceAndSection8Contracts)

    # -HUD Insured Multifamily Properties
    @property
    def hud_insured_multifamily_properties(self):
        return self.get_related_data(HUDInsuredMultifamilyProperties)

    # -HUD Multifamily Inspection Scores
    @property
    def hud_multifamily_inspection_scores(self):
        return self.get_related_data(HUDMultifamilyInspectionScores)

    # -LIHTC Data from PHFA
    @property
    def lihtc_data_from_phfa(self):
        return self.get_related_data(LIHTCDataFromPHFA)

    # -Demographics by Housing Project from PHFA
    @property
    def demographics_by_housing_project_from_phfa(self):
        return self.get_related_data(DemographicsByHousingProjectFromPHFA)

    # -Apartment Distributions, Income Limits, and Subsidies by Housing Project from PHFA
    @property
    def phfa_stats(self):
        return self.get_related_data(PHFAStats)

    @property
    def subsidy_info(self):
        return self.get_related_data(HouseCatSubsidyListing)

    def __str__(self):
        return f'{self.id}: {self.hud_property_name}'
