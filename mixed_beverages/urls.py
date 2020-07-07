from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.urls import path
from django.views.decorators.cache import cache_control
from django.views.generic import TemplateView

from mixed_beverages.apps.receipts.api import router

from .apps.lazy_geo import views

ONE_DAY = 86400
ONE_WEEK = ONE_DAY * 7


urlpatterns = [
    url(
        r"^robots.txt$",
        TemplateView.as_view(content_type="text/plain", template_name="robots.txt"),
    ),
    url(
        r"", include("mixed_beverages.apps.receipts.urls", namespace="mixed_beverages")
    ),
    path(
        "geo/data.geojson",
        cache_control(max_age=ONE_WEEK, public=True)(views.MarkerList.as_view()),
        name="geo_list",
    ),
    url(r"^api/", include(router.urls)),
    path("admin/", admin.site.urls),
]
