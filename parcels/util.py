# Mapping from usaddress fields to Parcel model fields
# https://usaddress.readthedocs.io/en/latest/
tag_mapping = {
    'AddressNumber': 'house_number',
    'AddressNumberPrefix': 'house_number',
    'AddressNumberSuffix': 'house_number',
    'StreetName': 'street_name',
    'StreetNamePreDirectional': 'street_name',
    'StreetNamePreModifier': 'street_name',
    'StreetNamePreType': 'street_name',
    'StreetNamePostDirectional': 'street_name',
    'StreetNamePostModifier': 'street_name',
    'StreetNamePostType': 'street_name',
    'LandmarkName': 'landmark_name',
    'USPSBoxGroupID': 'post_box',
    'USPSBoxGroupType': 'post_box',
    'USPSBoxID': 'post_box',
    'USPSBoxType': 'post_box',
    'BuildingName': 'building_name',
    'PlaceName': 'city',
    'StateName': 'state',
    'ZipCode': 'zip_code',

    # -- UNUSED FIELDS --
    # 'Recipient': 'NOT_USED',
    # 'CornerOf': 'address1',
    # 'IntersectionSeparator': 'address1',
    # 'OccupancyType': 'address2',
    # 'OccupancyIdentifier': 'address2',
    # 'SubaddressIdentifier': 'address2',
    # 'SubaddressType': 'address2',
}

# sales 5bbe6c55-bce6-4edb-9d04-68edeb6bf7b1
# ass appeals cb6a8441-0ed9-443d-aea1-a68e62f9a267
# assmt 518b583f-7cc8-4f60-94d0-174cc98310dc
