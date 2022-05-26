from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'taxonomy', views.TaxonomyViewSet)
router.register(r'domain', views.DomainViewSet)
router.register(r'subdomain', views.SubdomainViewSet)
router.register(r'topic', views.TopicViewSet)
router.register(r'indicator', views.IndicatorViewSet)
router.register(r'time-axis', views.TimeAxisViewSet)
router.register(r'variable', views.VariableViewSet)

urlpatterns = router.urls + []
