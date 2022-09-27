from typing import TypedDict


class CKANResource(TypedDict):
    mimetype: str
    cache_url: str
    hash: str
    description: str
    name: str
    format: str
    url: str
    datastore_active: bool
    cache_last_updated: str
    package_id: str
    created: str
    state: str
    mimetype_inner: str
    last_modified: str
    position: int
    revision_id: str
    url_type: str
    id: str
    resource_type: str
    size: str



class CKANPackage(TypedDict):
    display_name: str
    description: str
    image_display_url: str
    package_count: int
    created: str
    name: str
    is_organization: bool
    state: str
    extras: list[str]
    image_url: str
    groups: list[str]
    type: str
    title: str
    revision_id: str
    num_followers: int
    id: str
    tags: list[str]
    approval_status: str
    resources: list[CKANResource]
