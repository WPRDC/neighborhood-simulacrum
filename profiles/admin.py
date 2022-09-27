from django.contrib.admin import AdminSite


class CustomAdminSite(AdminSite):
    site_header = 'Neighborhood Simulacrum'
    site_title = 'Neighborhood Simulacrum'


