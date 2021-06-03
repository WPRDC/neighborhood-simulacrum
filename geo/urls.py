from django.urls import re_path
from rest_framework import routers
from . import views

router = routers.SimpleRouter()
router.register(r'blockGroup', views.BlockGroupViewSet, basename='blockgroup')
router.register(r'tract', views.TractViewSet, basename='tract')
router.register(r'countySubdivision', views.CountySubdivisionViewSet, basename='countysubdivision')
router.register(r'county', views.CountyViewSet, basename='county')
router.register(r'neighborhood', views.NeighborhoodViewSet, basename='neighborhood')
router.register(r'zcta', views.ZipCodeViewSet, basename='zcta')

urlpatterns = router.urls + [
    re_path(r'geog-types/?$', views.geog_list),
]
