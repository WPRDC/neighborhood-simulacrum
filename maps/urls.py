from django.urls import path
from rest_framework import routers
from . import views

router = routers.SimpleRouter()
router.register(r'data-layers', views.DataLayerViewSet)
router.register(r'map-layers', views.MapLayerViewSet)

urlpatterns = router.urls + [
    path('geojson/<slug:map_slug>.geojson',
         views.GeoJSONDataLayerView.as_view()),
]
