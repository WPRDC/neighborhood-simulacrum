import debug_toolbar
from django.contrib import admin
from django.urls import path, include
from rest_framework.schemas import get_schema_view

urlpatterns = [
  #  path('grappelli/', include('grappelli.urls')),
    path('_nested_admin/', include('nested_admin.urls')),
    path('_debug/', include(debug_toolbar.urls)),
    path('admin/', admin.site.urls),
    path('geo/', include('geo.urls')),
    path('maps/', include('maps.urls')),
    path('', include('indicators.urls')),
    path('openapi', get_schema_view(
        title="Neighborhood Simulacrum",
        url="https://api.profiles.wprdc.org/",
        description="API for neighborhood indicators and other civic open data.",
        version="0.0.1"
    ), name='openapi-schema'),
]
