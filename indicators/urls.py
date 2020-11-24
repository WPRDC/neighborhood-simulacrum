from rest_framework import routers
from . import views

router = routers.SimpleRouter()
router.register(r'domain', views.DomainViewSet)
router.register(r'subdomain', views.SubdomainViewSet)
router.register(r'indicator', views.IndicatorViewSet)
router.register(r'data-viz', views.DataVizViewSet)
router.register(r'series', views.SeriesViewSet)
router.register(r'variable', views.VariableViewSet)

urlpatterns = router.urls
