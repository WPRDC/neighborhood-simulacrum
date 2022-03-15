from django.urls import path
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'project', views.ProjectViewSet, basename='projectindex')
router.register(r'watchlist', views.WatchlistViewSet)

urlpatterns = router.urls + [
    path('projects.geojson', views.ProjectGeoJSONViewSet.as_view({'get': 'list'})),
    path('vector-map/', views.ProjectVectorTileViewSet.as_view()),
]
