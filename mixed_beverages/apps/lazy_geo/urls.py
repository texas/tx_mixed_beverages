from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^data.geojson$', views.marker_list, name='geo'),
]
