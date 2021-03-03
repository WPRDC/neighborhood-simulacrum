import debug_toolbar
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('grappelli/', include('grappelli.urls')),
    path('_nested_admin/', include('nested_admin.urls')),
    path('_debug/', include(debug_toolbar.urls)),
    path('admin/', admin.site.urls),
    path('geo/', include('geo.urls')),
    path('', include('indicators.urls')),

]
