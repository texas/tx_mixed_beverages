from django.conf.urls import patterns, include, url
from django.contrib import admin

from mixed_beverages.apps.receipts.api import router


urlpatterns = patterns('',
    url(r'^api/', include(router.urls)),
    url(r'^admin/', include(admin.site.urls)),
)
