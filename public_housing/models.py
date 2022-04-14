from datetime import date, timedelta, datetime
from functools import lru_cache
from typing import Type

from django.contrib.auth.models import User
from django.contrib.gis.db import models
from django.contrib.gis.geos import Point
from django.contrib.postgres.fields import ArrayField
from django.db.models import QuerySet, F, Q
from django.db.models.functions import Cast, Substr, Length

from profiles.abstract_models import DatastoreDataset, Described
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
    HousingDataset,
    ContractID,
    DevelopmentCode,
    FHALoanID,
    LIHTCProjectID,
    NormalizeStateID,
    PMIndx,
    LookupTable,
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


def get_risk_level_query_parts(lvl: str) -> (str, date):
    if lvl == 'future':
        return 'gt', date.today() + timedelta(days=365 * 5)
    n, dur = lvl[0], lvl[1:]
    days = -1
    if dur == 'mo':
        days = 31 * int(n)
    if dur == 'yr':
        days = 365 * int(n)
    return 'lt', date.today() + timedelta(days=days)


def get_fkeys(model: Type['LookupTable'], origin_id: int):
    """ returns a list of matching foreign keys to the model from project index with origin_id"""
    qs = model.objects.filter(projectindex_id=origin_id).values('projectidentifier_id')
    return [item['projectidentifier_id'] for item in qs]


TODAY = datetime.now().date()


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
    def filter_by_risk_level(
            queryset: QuerySet['ProjectIndex'],
            lvl: str
    ) -> QuerySet['ProjectIndex']:
        """ Finds subsidy listings that expire on or before `date` and returns ProjectIndexes that match """
        mthd, dt = get_risk_level_query_parts(lvl)
        matching_ids = [subsidy.property_id for subsidy
                        in HouseCatSubsidyListing.objects.filter(**{f'subsidy_expiration_date__{mthd}': dt})
                        if subsidy.subsidy_expiration_date is not None]
        return queryset.filter(property_id__in=matching_ids)

    @staticmethod
    def filter_by_lihtc_compliance(queryset: QuerySet['ProjectIndex'], lvl: str):
        """
        Filter showing properties in the initial LIHTC compliance period (years 0-15) from the date or year placed into service
        Filter showing properties in the LIHTC extended use period (years 15-30) from date placed into service
        :param queryset:
        :param lvl:
        :return:
        """
        _filter = {}
        if lvl == 'initial':
            # in the initial LIHTC compliance period (years 0-15) from the date or year placed into service
            _filter = {'lihtc_year_in_service__gte': (TODAY - timedelta(days=365 * 15)).year}
        elif lvl == 'extended':
            #  in the LIHTC extended use period (years 15-30) from date placed into service
            _filter = {
                'lihtc_year_in_service__range': (
                    (TODAY - timedelta(days=365 * 30)).year,
                    (TODAY - timedelta(days=365 * 15)).year
                )
            }
        elif lvl == 'initial-exp':
            # in year 13-15 from year placed into service (initial LIHTC compliance period expires soon)
            _filter = {
                'lihtc_year_in_service__range': (
                    (TODAY - timedelta(days=365 * 15)).year,
                    (TODAY - timedelta(days=365 * 13)).year
                )
            }
        elif lvl == 'extended-exp':
            # in year 27-30 from year placed into service (LIHTC extended use period expires soon)
            _filter = {
                'lihtc_year_in_service__range': (
                    (TODAY - timedelta(days=365 * 30)).year,
                    (TODAY - timedelta(days=365 * 27)).year
                )
            }
        else:
            return queryset
        # get all the possible lihtc ids
        lihtc_records = LIHTC.objects.filter(**_filter)
        lihtc_project_ids = [l.lihtc_project_id for l in lihtc_records]
        lihtc_normalized_state_ids = [l.normalized_state_id for l in lihtc_records]

        # find project index records that relate to these lihtc records
        lookup_records = LIHTCProjectID.objects.filter(
            projectidentifier_id__in=lihtc_project_ids + lihtc_normalized_state_ids)
        project_index_ids = [r.projectindex_id for r in lookup_records]

        return queryset.filter(id__in=project_index_ids)

    @staticmethod
    def filter_by_reac_score(queryset: QuerySet['ProjectIndex'], lvl: str):
        """ Filter by REAC score for HUD properties """
        max_score, min_score = None, None
        if lvl == 'failing':
            max_score = 60
        elif lvl == 'annual-inspection':
            max_score = 80
        elif lvl == 'minimal-inspection':
            min_score = 80
        else:
            # don't filter by default
            return queryset

        # make a filter based on the args provided
        mf_filter_args, d_filter_args = {}, {}
        if max_score is not None:
            mf_filter_args = {'score__lt': max_score}
            d_filter_args = {'inspection_score__lt': max_score}

        if min_score is not None:
            mf_filter_args = {**{'score__gte': min_score}, **mf_filter_args}
            d_filter_args = {**{'inspection_score__gte': min_score}, **d_filter_args}

        # filter querysets
        multi_fam_records = HUDMultifamilyInspectionScores.objects.annotate(
            # strip out int of score
            score=Cast(
                Substr(F('inspection_score'), 1, Length(F('inspection_score')) - 2),
                output_field=models.IntegerField())
        ).filter(**mf_filter_args)
        devel_records = HUDInspectionScores.objects.filter(**d_filter_args)

        # find project index records that relate to these inspection records
        dev_code_lookup = DevelopmentCode.objects.filter(
            projectidentifier_id__in=[d.development_code for d in devel_records]
        )
        project_index_ids = [r.projectindex_id for r in dev_code_lookup]
        property_ids = [mf.property_id for mf in multi_fam_records]

        return queryset.filter(Q(id__in=project_index_ids) | Q(property_id__in=property_ids))

    @staticmethod
    def filter_by_last_inspection(queryset: QuerySet['ProjectIndex'], lvl: str):
        """ Filter projects by last HUD inspection """
        if lvl == '3mos':
            time_back = timedelta(weeks=4 * 3)
        elif lvl == '6mos':
            time_back = timedelta(weeks=4 * 6)
        else:
            # don't filter by default
            return queryset

        multi_fam_records = HUDMultifamilyInspectionScores.objects.filter(inspection_date__gte=TODAY - time_back)
        devel_records = HUDInspectionScores.objects.filter(inspection_date__gte=TODAY - time_back)

        # find project index records that relate to these inspection records
        dev_code_lookup = DevelopmentCode.objects.filter(
            projectidentifier_id__in=[d.development_code for d in devel_records]
        )
        project_index_ids = [r.projectindex_id for r in dev_code_lookup]
        property_ids = [mf.property_id for mf in multi_fam_records]

        return queryset.filter(Q(id__in=project_index_ids) | Q(property_id__in=property_ids))

    @staticmethod
    def filter_by_funding_type(queryset: QuerySet['ProjectIndex'], lvl: str):
        """ Filters by source of funding - TBD """
        if lvl == 'public-housing':
            pass
        if lvl == 'multifamily':
            pass
        if lvl == 'lihtc':
            pass

        return queryset

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


class Account(models.Model):
    name = models.CharField(max_length=40)
    user = models.OneToOneField(User, on_delete=models.CASCADE)


class Watchlist(Described):
    account = models.OneToOneField(Account, on_delete=models.CASCADE)
    items = ArrayField(base_field=models.CharField(max_length=200))

    @property
    def user_name(self):
        return self.account.name

    @property
    def project_indices(self):
        return ProjectIndex.objects.filter(property_id__in=self.items)
