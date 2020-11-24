from django.urls import path
from . import views

urlpatterns = [
    path('region/', views.GetRegion.as_view(), name='get-region'),
]
