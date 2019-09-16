from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('glowstone.apps.index.urls', namespace='index')),
]
