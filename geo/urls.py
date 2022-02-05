from django.urls import re_path
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'blockGroup', views.BlockGroupViewSet, basename='blockgroup')
router.register(r'tract', views.TractViewSet, basename='tract')
router.register(r'countySubdivision', views.CountySubdivisionViewSet, basename='countysubdivision')
router.register(r'county', views.CountyViewSet, basename='county')
router.register(r'neighborhood', views.NeighborhoodViewSet, basename='neighborhood')
router.register(r'zcta', views.ZipCodeViewSet, basename='zcta')
router.register(r'', views.AdminRegionViewSet, basename='adminregion')

urlpatterns = [
    re_path(r'geog-types/?$', views.GeoLevelView.as_view()),
    re_path(r'geog-levels/?$', views.GeoLevelView.as_view()),
] + router.urls

# todo: make view that gets geo's by slug.  in fact, standardize all resource views to be accessible the same way
#   and then go over the API on the typescript end
