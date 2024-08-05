from django.apps import apps
from django.conf import settings
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("",include("core.urls")),
]

if apps.is_installed("debug_toolbar"):
    if settings.DEBUG:
        urlpatterns +=[
            path("__debug__",include("debug_toolbar.urls")),
        ]