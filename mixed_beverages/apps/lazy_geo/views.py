import json

from django.http import HttpResponseBadRequest, JsonResponse
from django.views.generic import DetailView
from djgeojson.views import GeoJSONLayerView
from mixed_beverages.apps.receipts import models

from .models import Correction
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
    # do I need to restrict to locations that are geocoded?
    model = models.Location
    template_name = 'lazy_geo/fixit.html'

    def data_as_json(self):
        if self.object.data:
            return json.dumps(self.object.data)
        return '{}'

    def post(self, request, **kwargs):
        obj = self.get_object()
        correction = Correction.objects.create_from_request(obj, request)
        correction.approve(request.user)
        return self.get(request, **kwargs)
