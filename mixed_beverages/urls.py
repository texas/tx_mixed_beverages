from django.conf.urls import include, url
from django.contrib import admin

from mixed_beverages.apps.receipts.api import router


urlpatterns = [
    url(r'', include('mixed_beverages.apps.receipts.urls',
        namespace='mixed_beverages')),
    url(r'^geo/', include('mixed_beverages.apps.lazy_geo.urls',
        namespace='lazy_geo')),
    url(r'^api/', include(router.urls)),
    url(r'^admin/', include(admin.site.urls)),
]
