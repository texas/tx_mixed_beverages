import json

from django.contrib.admin.views.decorators import staff_member_required
from django.urls import reverse
from django.db.models import Q
from django.http import (
    HttpResponseBadRequest,
    JsonResponse,
    HttpResponseRedirect,
    HttpResponseForbidden,
)
from django.utils.decorators import method_decorator
from django.views.generic import DetailView
from djgeojson.views import GeoJSONLayerView
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
        return JsonResponse(
            {
                "latitude": self.object.coordinate.y,
                "longitude": self.object.coordinate.x,
                "title": "{}: {}".format(
                    self.object.coordinate_quality,
                    self.object.get_coordinate_quality_display(),
                ),
            }
        )


class MarkerList(GeoJSONLayerView):
    queryset = models.Location.objects.filter(coordinate__isnull=False).exclude(
        Q(data__avg_total="0") | Q(data__avg_total="0.00")
    )
    geometry_field = "coordinate"
    precision = 6
    properties = ("coordinate_quality", "data", "name")
