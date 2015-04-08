from django.http import HttpResponseBadRequest, JsonResponse
from django.views.generic import DetailView
from mixed_beverages.apps.receipts import models
from djgeojson.views import GeoJSONLayerView

from .utils import GeocodeException


class AddressGeocode(DetailView):
    """Geocode a model on the fly."""
    model = models.Receipt

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        # WISHLIST this locks up a worker for some time
        try:
            self.object.geocode()
        except GeocodeException as e:
            return HttpResponseBadRequest(e)
        return JsonResponse({
            'latitude': self.object.coordinate.y,
            'longitude': self.object.coordinate.x,
            'title': '{}: {}'.format(
                self.object.coordinate_quality,
                self.object.get_coordinate_quality_display(),
            ),
        })


class MarkerList(GeoJSONLayerView):
    queryset = models.Location.objects.exclude(coordinate=None)
    geometry_field = 'coordinate'
    precision = 6
    properties = ('coordinate_quality', 'data',)


class FixDetail(DetailView):
    model = models.Receipt
    template_name = 'lazy_geo/fixit.html'
