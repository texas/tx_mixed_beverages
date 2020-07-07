from django.urls import path
from django.views.decorators.cache import cache_control

from . import views

ONE_DAY = 86400
ONE_WEEK = ONE_DAY * 7


app_name = "lazy_geo"
urlpatterns = [
    path(
        "data.geojson",
        cache_control(max_age=ONE_WEEK, public=True)(views.MarkerList.as_view()),
        name="geo",
    ),
]
