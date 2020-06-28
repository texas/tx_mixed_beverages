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
        "address",
        "city",
        "state",
        "zip",
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
    # List
    ######

    def display_name(self, obj):
        if obj.data:
            return obj.data["name"]

        return "-name-"

    def display_tax(self, obj):
        if obj.data:
            return obj.data["avg_tax"]

        return "-tax"

    list_display = ("display_name", "display_tax", "coordinate_quality")
    list_filter = ("coordinate_quality",)

    # Detail
    ########

    inlines = [
        ReceiptInline,
    ]
    save_on_top = True
    readonly_fields = ("data", "businesses")


@admin.register(models.Receipt)
class ReceiptAdmin(admin.ModelAdmin):
    list_display = ("name", "date", "total", "city", "zip")
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
                    "address",
                    ("city", "state", "zip"),
                    "county_code",
                )
            },
        ),
        ("Relations", {"fields": ("business", "location",)}),
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
        "address",
        "city",
        "state",
        "zip",
        "county_code",
        "business",
        "location",
    )
