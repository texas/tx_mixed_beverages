import os
from decimal import Decimal

import requests
from django.core.management.base import CommandError
from django.db.models import DecimalField, F, QuerySet
from django.db.models.fields.json import KeyTextTransform
from django.db.models.functions import Cast

from .models import Location

API_URL = "https://api.geocod.io/v1.7/geocode"
BATCH_SIZE = 10_000  # Geocodio's per-request maximum


def get_api_key() -> str:
    api_key = os.environ.get("GEOCODIO_API_KEY")
    if not api_key:
        raise CommandError("GEOCODIO_API_KEY is not set")
    return api_key


def order_by_recent_business(qs: QuerySet[Location]) -> QuerySet[Location]:
    """
    Annotate `avg_total` (see `utils.set_location_data`) and order by it,
    highest first.
    """
    return qs.annotate(
        avg_total=Cast(KeyTextTransform("avg_total", "data"), DecimalField())
    ).order_by(F("avg_total").desc(nulls_last=True), "pk")


def geocode(
    api_key: str, locations: list[Location]
) -> list[tuple[float, float, Decimal] | None]:
    """
    Batch geocode locations. Returns one entry per location, in order:
    (lat, lng, accuracy) of the best match, or None if there was no match.
    """
    results: list[tuple[float, float, Decimal] | None] = []
    for i in range(0, len(locations), BATCH_SIZE):
        chunk = locations[i : i + BATCH_SIZE]
        body = [
            {
                "street": x.street_address,
                "city": x.city,
                "state": x.state,
                "postal_code": x.zip,
            }
            for x in chunk
        ]
        response = requests.post(
            API_URL, params={"api_key": api_key}, json=body, timeout=300
        )
        response.raise_for_status()
        data = response.json()["results"]
        if len(data) != len(chunk):
            raise CommandError(f"Sent {len(chunk)} addresses, received {len(data)}")
        for result in data:  # same order as the input
            candidates = result["response"].get("results") or []
            if not candidates:
                results.append(None)
                continue
            best = candidates[0]
            results.append(
                (
                    best["location"]["lat"],
                    best["location"]["lng"],
                    Decimal(str(best["accuracy"])),
                )
            )
    return results
