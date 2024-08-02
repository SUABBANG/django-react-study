from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path("admin/", admin.site.urls),
    path(route="core/",view=include("core.urls")),
    path(route="hottrack/",view=include("hottrack.urls")),
    path(route="blog/",view=include("blog.urls")),
    path("",RedirectView.as_view(url="/hottrack/")), # 최상이 주소 리다이렉트
]

if settings.DEBUG:
    urlpatterns += [
        path("__debug__/", include("debug_toolbar.urls")),
    ]
