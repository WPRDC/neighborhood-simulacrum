from django.contrib.gis.db import models


class Parcel(models.Model):
    """ Master record for individual parcels known to this system. """
    parcel_id = models.CharField(max_length=24)

    # address
    house_number = models.CharField(max_length=20, null=True, blank=True)
    street_name = models.CharField(max_length=60, null=True, blank=True)
    city = models.CharField(max_length=60, null=True, blank=True)
    state = models.CharField(max_length=60, null=True, blank=True)
    zip_code = models.CharField(max_length=60, null=True, blank=True)

    # bonus address features
    landmark_name = models.CharField(max_length=60, null=True, blank=True)
    post_box = models.CharField(max_length=100, null=True, blank=True)
    building_name = models.CharField(max_length=60, null=True, blank=True)

    @property
    def address(self):
        return f'{self.house_number} {self.street_name} {self.city} {self.state}'

    @property
    def sales(self):
        return PropertySales.objects.filter(parid=self.parcel_id)


# Parcel Datasets
class PropertySales(models.Model):
    field_id = models.AutoField(db_column='_id', primary_key=True)  # Field renamed because it started with '_'.
    field_full_text = models.TextField(db_column='_full_text', blank=True,
                                       null=True)  # Field renamed because it started with '_'. This field type is a guess.
    parid = models.TextField(db_column='PARID', blank=True, null=True)  # Field name made lowercase.
    propertyhousenum = models.IntegerField(db_column='PROPERTYHOUSENUM', blank=True,
                                           null=True)  # Field name made lowercase.
    propertyfraction = models.TextField(db_column='PROPERTYFRACTION', blank=True,
                                        null=True)  # Field name made lowercase.
    propertyaddressdir = models.TextField(db_column='PROPERTYADDRESSDIR', blank=True,
                                          null=True)  # Field name made lowercase.
    propertyaddressstreet = models.TextField(db_column='PROPERTYADDRESSSTREET', blank=True,
                                             null=True)  # Field name made lowercase.
    propertyaddresssuf = models.TextField(db_column='PROPERTYADDRESSSUF', blank=True,
                                          null=True)  # Field name made lowercase.
    propertyaddressunitdesc = models.TextField(db_column='PROPERTYADDRESSUNITDESC', blank=True,
                                               null=True)  # Field name made lowercase.
    propertyunitno = models.TextField(db_column='PROPERTYUNITNO', blank=True, null=True)  # Field name made lowercase.
    propertycity = models.TextField(db_column='PROPERTYCITY', blank=True, null=True)  # Field name made lowercase.
    propertystate = models.TextField(db_column='PROPERTYSTATE', blank=True, null=True)  # Field name made lowercase.
    propertyzip = models.FloatField(db_column='PROPERTYZIP', blank=True, null=True)  # Field name made lowercase.
    schoolcode = models.TextField(db_column='SCHOOLCODE', blank=True, null=True)  # Field name made lowercase.
    schooldesc = models.TextField(db_column='SCHOOLDESC', blank=True, null=True)  # Field name made lowercase.
    municode = models.TextField(db_column='MUNICODE', blank=True, null=True)  # Field name made lowercase.
    munidesc = models.TextField(db_column='MUNIDESC', blank=True, null=True)  # Field name made lowercase.
    recorddate = models.DateField(db_column='RECORDDATE', blank=True, null=True)  # Field name made lowercase.
    saledate = models.DateField(db_column='SALEDATE', blank=True, null=True)  # Field name made lowercase.
    price = models.FloatField(db_column='PRICE', blank=True, null=True)  # Field name made lowercase.
    deedbook = models.TextField(db_column='DEEDBOOK', blank=True, null=True)  # Field name made lowercase.
    deedpage = models.TextField(db_column='DEEDPAGE', blank=True, null=True)  # Field name made lowercase.
    salecode = models.TextField(db_column='SALECODE', blank=True, null=True)  # Field name made lowercase.
    saledesc = models.TextField(db_column='SALEDESC', blank=True, null=True)  # Field name made lowercase.
    instrtyp = models.TextField(db_column='INSTRTYP', blank=True, null=True)  # Field name made lowercase.
    instrtypdesc = models.TextField(db_column='INSTRTYPDESC', blank=True, null=True)  # Field name made lowercase.
    field_geom = models.PointField(db_column='_geom', blank=True,
                                   null=True)  # Field renamed because it started with '_'.
    field_the_geom_webmercator = models.PointField(db_column='_the_geom_webmercator', srid=3857, blank=True,
                                                   null=True)  # Field renamed because it started with '_'.

    class Meta:
        managed = False
        db_table = '5bbe6c55-bce6-4edb-9d04-68edeb6bf7b1'
        unique_together = (
            ('parid', 'recorddate', 'saledate', 'deedbook', 'deedpage', 'instrtyp', 'price', 'salecode'),)


class PropertyAssessmentAppeals(models.Model):
    field_id = models.AutoField(db_column='_id', primary_key=True)  # Field renamed because it started with '_'.
    field_full_text = models.TextField(db_column='_full_text', blank=True,
                                       null=True)  # Field renamed because it started with '_'. This field type is a guess.
    parcel_id = models.TextField(db_column='PARCEL ID', blank=True,
                                 null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    tax_year = models.TextField(db_column='TAX YEAR', blank=True,
                                null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    class_field = models.TextField(db_column='CLASS', blank=True,
                                   null=True)  # Field name made lowercase. Field renamed because it was a Python reserved word.
    class_group = models.TextField(db_column='CLASS GROUP', blank=True,
                                   null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    tax_status = models.TextField(db_column='TAX_STATUS', blank=True, null=True)  # Field name made lowercase.
    muni_code = models.TextField(db_column='MUNI_CODE', blank=True, null=True)  # Field name made lowercase.
    muni_name = models.TextField(db_column='MUNI_NAME', blank=True, null=True)  # Field name made lowercase.
    school_code = models.TextField(db_column='SCHOOL_CODE', blank=True, null=True)  # Field name made lowercase.
    school_district = models.TextField(db_column='SCHOOL_DISTRICT', blank=True, null=True)  # Field name made lowercase.
    hearing_type = models.TextField(db_column='HEARING_TYPE', blank=True, null=True)  # Field name made lowercase.
    complainant = models.TextField(db_column='COMPLAINANT', blank=True, null=True)  # Field name made lowercase.
    hearing_status = models.TextField(db_column='HEARING_STATUS', blank=True, null=True)  # Field name made lowercase.
    status = models.TextField(db_column='STATUS', blank=True, null=True)  # Field name made lowercase.
    pre_appeal_land = models.TextField(db_column='PRE APPEAL LAND', blank=True,
                                       null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    pre_appeal_bldg = models.TextField(db_column='PRE APPEAL BLDG', blank=True,
                                       null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    pre_appeal_total = models.TextField(db_column='PRE APPEAL TOTAL', blank=True,
                                        null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    post_appeal_land = models.TextField(db_column='POST APPEAL LAND', blank=True,
                                        null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    post_appeal_bldg = models.TextField(db_column='POST APPEAL BLDG', blank=True,
                                        null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    post_appeal_total = models.TextField(db_column='POST APPEAL TOTAL', blank=True,
                                         null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    hearing_change_amount = models.TextField(db_column='HEARING CHANGE AMOUNT', blank=True,
                                             null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    last_update_reason = models.TextField(db_column='LAST UPDATE REASON', blank=True,
                                          null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    current_land_value = models.TextField(db_column='CURRENT LAND VALUE', blank=True,
                                          null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    current_bldg_value = models.TextField(db_column='CURRENT BLDG VALUE', blank=True,
                                          null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    current_total_value = models.TextField(db_column='CURRENT TOTAL VALUE', blank=True,
                                           null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    current_value_vs_pre_appeal = models.TextField(db_column='CURRENT VALUE vs PRE APPEAL', blank=True,
                                                   null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    hearing_date = models.TextField(db_column='HEARING DATE', blank=True,
                                    null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    dispo_date = models.TextField(db_column='DISPO DATE', blank=True,
                                  null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    elapsed_days = models.TextField(db_column='ELAPSED_DAYS', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'cb6a8441-0ed9-443d-aea1-a68e62f9a267'


class PropertyAssessments(models.Model):
    field_id = models.AutoField(db_column='_id', primary_key=True)  # Field renamed because it started with '_'.
    field_full_text = models.TextField(db_column='_full_text', blank=True,
                                       null=True)  # Field renamed because it started with '_'. This field type is a guess.
    parid = models.TextField(db_column='PARID', unique=True, blank=True, null=True)  # Field name made lowercase.
    propertyhousenum = models.TextField(db_column='PROPERTYHOUSENUM', blank=True,
                                        null=True)  # Field name made lowercase.
    propertyfraction = models.TextField(db_column='PROPERTYFRACTION', blank=True,
                                        null=True)  # Field name made lowercase.
    propertyaddress = models.TextField(db_column='PROPERTYADDRESS', blank=True, null=True)  # Field name made lowercase.
    propertycity = models.TextField(db_column='PROPERTYCITY', blank=True, null=True)  # Field name made lowercase.
    propertystate = models.TextField(db_column='PROPERTYSTATE', blank=True, null=True)  # Field name made lowercase.
    propertyunit = models.TextField(db_column='PROPERTYUNIT', blank=True, null=True)  # Field name made lowercase.
    propertyzip = models.TextField(db_column='PROPERTYZIP', blank=True, null=True)  # Field name made lowercase.
    municode = models.TextField(db_column='MUNICODE', blank=True, null=True)  # Field name made lowercase.
    munidesc = models.TextField(db_column='MUNIDESC', blank=True, null=True)  # Field name made lowercase.
    schoolcode = models.TextField(db_column='SCHOOLCODE', blank=True, null=True)  # Field name made lowercase.
    schooldesc = models.TextField(db_column='SCHOOLDESC', blank=True, null=True)  # Field name made lowercase.
    legal1 = models.TextField(db_column='LEGAL1', blank=True, null=True)  # Field name made lowercase.
    legal2 = models.TextField(db_column='LEGAL2', blank=True, null=True)  # Field name made lowercase.
    legal3 = models.TextField(db_column='LEGAL3', blank=True, null=True)  # Field name made lowercase.
    neighcode = models.TextField(db_column='NEIGHCODE', blank=True, null=True)  # Field name made lowercase.
    neighdesc = models.TextField(db_column='NEIGHDESC', blank=True, null=True)  # Field name made lowercase.
    taxcode = models.TextField(db_column='TAXCODE', blank=True, null=True)  # Field name made lowercase.
    taxdesc = models.TextField(db_column='TAXDESC', blank=True, null=True)  # Field name made lowercase.
    taxsubcode = models.TextField(db_column='TAXSUBCODE', blank=True, null=True)  # Field name made lowercase.
    taxsubcode_desc = models.TextField(db_column='TAXSUBCODE_DESC', blank=True, null=True)  # Field name made lowercase.
    ownercode = models.TextField(db_column='OWNERCODE', blank=True, null=True)  # Field name made lowercase.
    ownerdesc = models.TextField(db_column='OWNERDESC', blank=True, null=True)  # Field name made lowercase.
    class_field = models.TextField(db_column='CLASS', blank=True,
                                   null=True)  # Field name made lowercase. Field renamed because it was a Python reserved word.
    classdesc = models.TextField(db_column='CLASSDESC', blank=True, null=True)  # Field name made lowercase.
    usecode = models.TextField(db_column='USECODE', blank=True, null=True)  # Field name made lowercase.
    usedesc = models.TextField(db_column='USEDESC', blank=True, null=True)  # Field name made lowercase.
    lotarea = models.FloatField(db_column='LOTAREA', blank=True, null=True)  # Field name made lowercase.
    homesteadflag = models.TextField(db_column='HOMESTEADFLAG', blank=True, null=True)  # Field name made lowercase.
    cleangreen = models.TextField(db_column='CLEANGREEN', blank=True, null=True)  # Field name made lowercase.
    farmsteadflag = models.TextField(db_column='FARMSTEADFLAG', blank=True, null=True)  # Field name made lowercase.
    abatementflag = models.TextField(db_column='ABATEMENTFLAG', blank=True, null=True)  # Field name made lowercase.
    recorddate = models.TextField(db_column='RECORDDATE', blank=True, null=True)  # Field name made lowercase.
    saledate = models.TextField(db_column='SALEDATE', blank=True, null=True)  # Field name made lowercase.
    saleprice = models.FloatField(db_column='SALEPRICE', blank=True, null=True)  # Field name made lowercase.
    salecode = models.TextField(db_column='SALECODE', blank=True, null=True)  # Field name made lowercase.
    saledesc = models.TextField(db_column='SALEDESC', blank=True, null=True)  # Field name made lowercase.
    deedbook = models.TextField(db_column='DEEDBOOK', blank=True, null=True)  # Field name made lowercase.
    deedpage = models.TextField(db_column='DEEDPAGE', blank=True, null=True)  # Field name made lowercase.
    prevsaledate = models.TextField(db_column='PREVSALEDATE', blank=True, null=True)  # Field name made lowercase.
    prevsaleprice = models.FloatField(db_column='PREVSALEPRICE', blank=True, null=True)  # Field name made lowercase.
    prevsaledate2 = models.TextField(db_column='PREVSALEDATE2', blank=True, null=True)  # Field name made lowercase.
    prevsaleprice2 = models.FloatField(db_column='PREVSALEPRICE2', blank=True, null=True)  # Field name made lowercase.
    changenoticeaddress1 = models.TextField(db_column='CHANGENOTICEADDRESS1', blank=True,
                                            null=True)  # Field name made lowercase.
    changenoticeaddress2 = models.TextField(db_column='CHANGENOTICEADDRESS2', blank=True,
                                            null=True)  # Field name made lowercase.
    changenoticeaddress3 = models.TextField(db_column='CHANGENOTICEADDRESS3', blank=True,
                                            null=True)  # Field name made lowercase.
    changenoticeaddress4 = models.TextField(db_column='CHANGENOTICEADDRESS4', blank=True,
                                            null=True)  # Field name made lowercase.
    countybuilding = models.FloatField(db_column='COUNTYBUILDING', blank=True, null=True)  # Field name made lowercase.
    countyland = models.FloatField(db_column='COUNTYLAND', blank=True, null=True)  # Field name made lowercase.
    countytotal = models.FloatField(db_column='COUNTYTOTAL', blank=True, null=True)  # Field name made lowercase.
    countyexemptbldg = models.FloatField(db_column='COUNTYEXEMPTBLDG', blank=True,
                                         null=True)  # Field name made lowercase.
    localbuilding = models.FloatField(db_column='LOCALBUILDING', blank=True, null=True)  # Field name made lowercase.
    localland = models.FloatField(db_column='LOCALLAND', blank=True, null=True)  # Field name made lowercase.
    localtotal = models.FloatField(db_column='LOCALTOTAL', blank=True, null=True)  # Field name made lowercase.
    fairmarketbuilding = models.FloatField(db_column='FAIRMARKETBUILDING', blank=True,
                                           null=True)  # Field name made lowercase.
    fairmarketland = models.FloatField(db_column='FAIRMARKETLAND', blank=True, null=True)  # Field name made lowercase.
    fairmarkettotal = models.FloatField(db_column='FAIRMARKETTOTAL', blank=True,
                                        null=True)  # Field name made lowercase.
    style = models.TextField(db_column='STYLE', blank=True, null=True)  # Field name made lowercase.
    styledesc = models.TextField(db_column='STYLEDESC', blank=True, null=True)  # Field name made lowercase.
    stories = models.TextField(db_column='STORIES', blank=True, null=True)  # Field name made lowercase.
    yearblt = models.FloatField(db_column='YEARBLT', blank=True, null=True)  # Field name made lowercase.
    exteriorfinish = models.TextField(db_column='EXTERIORFINISH', blank=True, null=True)  # Field name made lowercase.
    extfinish_desc = models.TextField(db_column='EXTFINISH_DESC', blank=True, null=True)  # Field name made lowercase.
    roof = models.TextField(db_column='ROOF', blank=True, null=True)  # Field name made lowercase.
    roofdesc = models.TextField(db_column='ROOFDESC', blank=True, null=True)  # Field name made lowercase.
    basement = models.TextField(db_column='BASEMENT', blank=True, null=True)  # Field name made lowercase.
    basementdesc = models.TextField(db_column='BASEMENTDESC', blank=True, null=True)  # Field name made lowercase.
    grade = models.TextField(db_column='GRADE', blank=True, null=True)  # Field name made lowercase.
    gradedesc = models.TextField(db_column='GRADEDESC', blank=True, null=True)  # Field name made lowercase.
    condition = models.TextField(db_column='CONDITION', blank=True, null=True)  # Field name made lowercase.
    conditiondesc = models.TextField(db_column='CONDITIONDESC', blank=True, null=True)  # Field name made lowercase.
    cdu = models.TextField(db_column='CDU', blank=True, null=True)  # Field name made lowercase.
    cdudesc = models.TextField(db_column='CDUDESC', blank=True, null=True)  # Field name made lowercase.
    totalrooms = models.FloatField(db_column='TOTALROOMS', blank=True, null=True)  # Field name made lowercase.
    bedrooms = models.FloatField(db_column='BEDROOMS', blank=True, null=True)  # Field name made lowercase.
    fullbaths = models.FloatField(db_column='FULLBATHS', blank=True, null=True)  # Field name made lowercase.
    halfbaths = models.FloatField(db_column='HALFBATHS', blank=True, null=True)  # Field name made lowercase.
    heatingcooling = models.TextField(db_column='HEATINGCOOLING', blank=True, null=True)  # Field name made lowercase.
    heatingcoolingdesc = models.TextField(db_column='HEATINGCOOLINGDESC', blank=True,
                                          null=True)  # Field name made lowercase.
    fireplaces = models.FloatField(db_column='FIREPLACES', blank=True, null=True)  # Field name made lowercase.
    bsmtgarage = models.TextField(db_column='BSMTGARAGE', blank=True, null=True)  # Field name made lowercase.
    finishedlivingarea = models.FloatField(db_column='FINISHEDLIVINGAREA', blank=True,
                                           null=True)  # Field name made lowercase.
    cardnumber = models.FloatField(db_column='CARDNUMBER', blank=True, null=True)  # Field name made lowercase.
    alt_id = models.TextField(db_column='ALT_ID', blank=True, null=True)  # Field name made lowercase.
    taxyear = models.FloatField(db_column='TAXYEAR', blank=True, null=True)  # Field name made lowercase.
    asofdate = models.DateField(db_column='ASOFDATE', blank=True, null=True)  # Field name made lowercase.
    municipality = models.TextField(db_column='MUNICIPALITY', blank=True, null=True)  # Field name made lowercase.
    neighborhood = models.TextField(db_column='NEIGHBORHOOD', blank=True, null=True)  # Field name made lowercase.
    pgh_council_district = models.TextField(db_column='PGH_COUNCIL_DISTRICT', blank=True,
                                            null=True)  # Field name made lowercase.
    pgh_ward = models.TextField(db_column='PGH_WARD', blank=True, null=True)  # Field name made lowercase.
    pgh_public_works_division = models.TextField(db_column='PGH_PUBLIC_WORKS_DIVISION', blank=True,
                                                 null=True)  # Field name made lowercase.
    pgh_police_zone = models.TextField(db_column='PGH_POLICE_ZONE', blank=True, null=True)  # Field name made lowercase.
    pgh_fire_zone = models.TextField(db_column='PGH_FIRE_ZONE', blank=True, null=True)  # Field name made lowercase.
    tract = models.TextField(db_column='TRACT', blank=True, null=True)  # Field name made lowercase.
    block_group = models.TextField(db_column='BLOCK_GROUP', blank=True, null=True)  # Field name made lowercase.
    field_geom = models.PointField(db_column='_geom', blank=True,
                                   null=True)  # Field renamed because it started with '_'.
    field_the_geom_webmercator = models.PointField(db_column='_the_geom_webmercator', srid=3857, blank=True,
                                                   null=True)  # Field renamed because it started with '_'.

    class Meta:
        managed = False
        db_table = '518b583f-7cc8-4f60-94d0-174cc98310dc'
