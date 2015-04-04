from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^data.geojson$', views.MarkerList.as_view(), name='geo'),
]
