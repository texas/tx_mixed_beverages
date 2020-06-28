from django.contrib import admin
from django.contrib.gis.admin import GeoModelAdmin

from . import models


class ReceiptInline(admin.TabularInline):
    extra = 0
    model = models.Receipt
    fields = (
        "name",
        "tabc_permit",
        "date",
        "total",
        "location",
    )
    readonly_fields = fields


@admin.register(models.Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    ordering = ("name",)
    inlines = [ReceiptInline]


@admin.register(models.Location)
class LocationAdmin(GeoModelAdmin):
    list_display = ("street_address", "city", "state", "zip")
    list_filter = ("coordinate_quality",)

    # Detail
    ########

    inlines = [
        ReceiptInline,
    ]
    save_on_top = True
    readonly_fields = ("street_address", "city", "state", "zip", "data", "businesses")


@admin.register(models.Receipt)
class ReceiptAdmin(admin.ModelAdmin):
    list_display = ("name", "date", "total")
    search_fields = ("name",)
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "name",
                    "tax_number",
                    "tabc_permit",
                    "date",
                    ("liquor", "wine", "beer", "cover", "total"),
                )
            },
        ),
        (
            "Location",
            {
                "fields": (
                    "location_name",
                    "location_number",
                    "location",
                    "county_code",
                )
            },
        ),
        ("Relations", {"fields": ("business",)}),
    )
    readonly_fields = (
        "name",
        "tax_number",
        "tabc_permit",
        "date",
        "liquor",
        "wine",
        "beer",
        "cover",
        "total",
        "location_name",
        "location_number",
        "county_code",
        "business",
        "location",
    )
