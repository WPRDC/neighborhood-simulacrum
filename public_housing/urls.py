from django.urls import path
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'project', views.ProjectViewSet, basename='projectindex')

urlpatterns = router.urls + [
    path('projects.geojson', views.ProjectGeoJSONViewSet.as_view({'get': 'list'})),
    path('vector-map/', views.ProjectVectorTileViewSet.as_view()),
    path('vector-map-test/', views.ProjectVectorTestTileViewSet.as_view())
]
