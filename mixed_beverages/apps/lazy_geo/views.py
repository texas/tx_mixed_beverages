from django.core.serializers import serialize
from django.http import HttpResponseBadRequest, HttpResponse, JsonResponse
from django.views.generic import DetailView
from mixed_beverages.apps.receipts import models

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


def marker_list(request):
    queryset = (models.Location.objects.exclude(coordinate=None))
    data = serialize('geojson', queryset,
        geometry_field='coordinate',
        fields=('coordinate_quality', 'data'))
    return HttpResponse(data, content_type='application/json')
