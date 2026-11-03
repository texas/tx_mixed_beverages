"""
Canned, read-only ORM queries for agents and humans.

Run with `./manage.py query` (lists them) or `./manage.py query <name> k=v`.
To add one, write a function decorated with `@canned`: the docstring is its
description, its annotated keyword arguments are its parameters, and it
returns something `json.dumps(..., default=str)` can serialize.
"""

from collections.abc import Callable
from decimal import Decimal
from typing import Any

from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.db.models import Count, QuerySet

from . import geocodio
from .models import Location, Receipt

QUERIES: dict[str, Callable[..., Any]] = {}
BASE_URL = "http://localhost:8000"  # where `make dev` serves the map


def canned[F: Callable[..., Any]](fn: F) -> F:
    QUERIES[fn.__name__] = fn
    return fn


def _location_row(x: Location) -> dict[str, Any]:
    return {
        "pk": x.pk,
        "name": x.name,
        "address": x.address.replace("\n", ", "),
        "avg_total": x.avg_total,
        "coordinate_quality": x.coordinate_quality,
        "lat": x.coordinate.y if x.coordinate else None,
        "lng": x.coordinate.x if x.coordinate else None,
        "url": BASE_URL + x.get_absolute_url() if x.coordinate else None,
    }


def _rows(qs: QuerySet[Location], limit: int) -> list[dict[str, Any]]:
    return [_location_row(x) for x in geocodio.order_by_recent_business(qs)[:limit]]


@canned
def geocode_summary() -> dict[str, int]:
    """Counts of locations by geocoding state."""
    qs = geocodio.order_by_recent_business(Location.objects.all())
    missing = qs.filter(coordinate__isnull=True)
    located = qs.filter(coordinate__isnull=False)
    return {
        "locations": qs.count(),
        "missing_coordinate": missing.count(),
        "missing_coordinate_active": missing.filter(avg_total__gt=0).count(),
        "missing_coordinate_idle": missing.exclude(avg_total__gt=0).count(),
        "quality_at_least_0.9": located.filter(coordinate_quality__gte="0.9").count(),
        "quality_0.6_to_0.9": located.filter(
            coordinate_quality__gte="0.6", coordinate_quality__lt="0.9"
        ).count(),
        "quality_below_0.6": located.filter(coordinate_quality__lt="0.6").count(),
    }


@canned
def low_quality(limit: int = 20, max_quality: Decimal = Decimal("0.6")) -> list:
    """Located locations with quality below max_quality, busiest first."""
    return _rows(
        Location.objects.filter(
            coordinate__isnull=False, coordinate_quality__lt=max_quality
        ),
        limit,
    )


@canned
def near(
    lat: float,
    lng: float,
    radius_km: float = 5.0,
    limit: int = 20,
    worst_first: int = 1,
) -> list:
    """
    Located locations within radius_km of a point. worst_first=1 sorts lowest
    quality first, then nearest; worst_first=0 sorts nearest first.
    """
    point = Point(x=lng, y=lat, srid=4326)
    qs = geocodio.order_by_recent_business(
        Location.objects.filter(coordinate__distance_lte=(point, D(km=radius_km)))
    ).annotate(distance=Distance("coordinate", point))
    order = ["distance", "pk"]
    if worst_first:
        order = ["coordinate_quality", *order]
    return [
        {**_location_row(x), "distance_km": round(x.distance.km, 2)}
        for x in qs.order_by(*order)[:limit]
    ]


@canned
def unmatched(limit: int = 20) -> list:
    """Active locations without coordinates, busiest first."""
    qs = geocodio.order_by_recent_business(
        Location.objects.filter(coordinate__isnull=True)
    ).filter(avg_total__gt=0)
    return [_location_row(x) for x in qs[:limit]]


@canned
def top_locations(limit: int = 20) -> list:
    """Locations with the highest recent average monthly receipts."""
    return _rows(Location.objects.all(), limit)


@canned
def find_locations(name: str = "", city: str = "", limit: int = 20) -> list:
    """Locations whose name and city contain the given text (case-insensitive)."""
    return _rows(
        Location.objects.filter(name__icontains=name, city__icontains=city), limit
    )


@canned
def location(pk: int, receipts: int = 6) -> dict[str, Any]:
    """One location with its most recent receipts."""
    obj = geocodio.order_by_recent_business(Location.objects.filter(pk=pk)).get()
    recent = Receipt.objects.filter(location=obj).values(
        "date", "total", "liquor", "wine", "beer", "cover"
    )[:receipts]
    return {
        **_location_row(obj),
        "receipt_count": Receipt.objects.filter(location=obj).count(),
        "recent_receipts": list(recent),
    }


@canned
def locations_by_city(limit: int = 20) -> list:
    """Cities with the most locations."""
    return list(
        Location.objects.values("city")
        .annotate(locations=Count("pk"))
        .order_by("-locations", "city")[:limit]
    )
