import debug_toolbar
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path('_nested_admin/', include('nested_admin.urls')),
    path('_debug/', include(debug_toolbar.urls)),
    path('admin/', admin.site.urls),
    path('geo/', include('geo.urls')),
    path('maps/', include('maps.urls')),
    path('public-housing/', include('public_housing.urls')),
    path('', include('indicators.urls')),
    path('schema/', SpectacularAPIView.as_view(api_version='0.0.1'), name='schema'),
    path('schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path('markdownx/', include('markdownx.urls')),
]
