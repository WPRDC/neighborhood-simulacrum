from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'parcel', views.ParcelViewSet)
urlpatterns = router.urls + []
