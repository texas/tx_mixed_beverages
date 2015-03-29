from django.http import HttpResponseBadRequest, JsonResponse
from django.views.generic import DetailView
from mixed_beverages.apps.receipts import models

from .utils import GeocodeException


class AddressGeocode(DetailView, JsonResponse):
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
