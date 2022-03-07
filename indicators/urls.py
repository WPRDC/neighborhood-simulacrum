from django.urls import path
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'taxonomy', views.TaxonomyViewSet)
router.register(r'domain', views.DomainViewSet)
router.register(r'subdomain', views.SubdomainViewSet)
router.register(r'indicator', views.IndicatorViewSet)
router.register(r'data-viz', views.DataVizViewSet)
router.register(r'time-axis', views.TimeAxisViewSet)
router.register(r'variable', views.VariableViewSet)

urlpatterns = router.urls + [
    path('map_layer/<slug:geog_type_id>:<int:data_viz_id>:<int:variable_id>.geojson', views.GeoJSONWithDataView.as_view()),
    # path('tiles/<slug:geog_type_id>/<int:data_viz_id>/<int:variable_id>/<int:zoom>/<int:x>/<int:y>.mvt',
    #      views.mvt_tiles),
]
