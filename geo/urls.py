from django.urls import path
from rest_framework import routers
from . import views

router = routers.SimpleRouter()
router.register(r'blockGroup', views.BlockGroupViewSet, basename='blockgroup')
router.register(r'tract', views.TractViewSet, basename='tract')
router.register(r'countySubdivision', views.CountySubdivisionViewSet, basename='countysubdivision')
router.register(r'county', views.CountyViewSet, basename='county')

urlpatterns = router.urls + [
    path('geog-types', views.geog_list),
]
