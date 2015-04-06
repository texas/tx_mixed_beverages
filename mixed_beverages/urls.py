from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic import TemplateView

from mixed_beverages.apps.receipts.api import router


urlpatterns = [
    url(r'^robots.txt$', TemplateView.as_view(
        content_type='text/plain', template_name='robots.txt')),
    url(r'', include('mixed_beverages.apps.receipts.urls',
        namespace='mixed_beverages')),
    url(r'^geo/', include('mixed_beverages.apps.lazy_geo.urls',
        namespace='lazy_geo')),
    url(r'^api/', include(router.urls)),
]

if settings.DEBUG:
    urlpatterns += [
        url(r'^admin/', include(admin.site.urls)),
    ]
