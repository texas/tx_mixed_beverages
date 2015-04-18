from django.conf.urls import url
from django.views.decorators.cache import cache_control

from . import views

ONE_DAY = 86400
ONE_WEEK = ONE_DAY * 7


urlpatterns = [
    url(r'^data.geojson$',
        cache_control(max_age=ONE_WEEK, public=True)(views.MarkerList.as_view()),
        name='geo'),
    url(r'^fix/(?P<pk>\d+)/$', views.FixDetail.as_view(), name='fixit'),
    url(r'^correction/(?P<pk>\d+)/$', views.CorrectionDetail.as_view(),
        name='correction-detail'),
]
