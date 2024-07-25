# hottrack/urls.py

from django.urls import path
from . import views
from . import converters  # noqa


urlpatterns = [
    path(route="", view=views.index),
    path(route="archives/<date:release_date>", view=views.index),
    path(route="<int:pk>/cover.png", view=views.cover_png),
    path(route="export.csv", view=views.export_csv),
    path(route=r"^export\.(?P<format>(csv|xlsx))$", view=views.export, name="export"),
]
