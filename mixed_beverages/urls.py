from django.contrib import admin
from django.urls import include, path
from django.views.decorators.cache import cache_control
from django.views.generic import TemplateView

from .apps.lazy_geo import views

ONE_DAY = 86400
ONE_WEEK = ONE_DAY * 7


urlpatterns = [
    path(
        "robots.txt",
        TemplateView.as_view(content_type="text/plain", template_name="robots.txt"),
    ),
    path(
        "", include("mixed_beverages.apps.receipts.urls", namespace="mixed_beverages")
    ),
    path(
        "location/all.geojson",
        cache_control(max_age=ONE_WEEK, public=True)(views.MarkerList.as_view()),
        name="geo_list",
    ),
    path(
        "location/<int:pk>.json",
        cache_control(max_age=ONE_WEEK, public=True)(views.location_detail),
        name="location",
    ),
    path("admin/", admin.site.urls),
]
