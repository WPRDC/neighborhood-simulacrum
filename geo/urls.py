from django.urls import path
from rest_framework import routers
from . import views

router = routers.SimpleRouter()
router.register(r'blockGroup', views.BlockGroupViewSet)
router.register(r'tract', views.TractViewSet)
router.register(r'countySubdivision', views.CountySubdivisionViewSet)
router.register(r'county', views.CountyViewSet)

urlpatterns = router.urls + [
    path('region/', views.GetRegion.as_view(), name='get-region'),
]
