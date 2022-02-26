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
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.generic import DetailView
from djgeojson.views import GeoJSONLayerView
from mixed_beverages.apps.receipts import models


class MarkerList(GeoJSONLayerView):
    queryset = models.Location.objects.filter(coordinate__isnull=False).exclude(
        Q(data__avg_total="0") | Q(data__avg_total="0.00")
    )
    geometry_field = "coordinate"
    precision = 6
    properties = ("coordinate_quality", "data", "name")


def location_detail(request, pk: str):
    location = get_object_or_404(models.Location, pk=pk)
    receipts = [
        {
            "name": x.location_name,
            "date": x.date,
            "liquor": x.liquor,
            "wine": x.wine,
            "beer": x.beer,
            "cover": x.cover,
            "total": x.total,
        }
        for x in location.receipts.all().order_by("-date")
    ]
    return JsonResponse(
        {
            "id": location.id,
            "name": location.name,
            "data": location.data,
            "receipts": receipts,
        }
    )
