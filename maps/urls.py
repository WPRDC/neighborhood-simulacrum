from django.urls import path
from rest_framework import routers
from . import views

router = routers.SimpleRouter()
router.register(r'data-layers', views.DataLayerViewSet)

urlpatterns = router.urls + [
    path('geojson/<slug:map_slug>.geojson',
         views.GeoJSONDataLayerView.as_view()),
]
