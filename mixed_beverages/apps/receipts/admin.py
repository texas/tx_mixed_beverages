from django.contrib import admin
from django.contrib.gis.admin import GeoModelAdmin
from django.urls import reverse
from django.utils.safestring import mark_safe

from . import models


class ReceiptInline(admin.TabularInline):
    extra = 0
    model = models.Receipt
    fields = (
        "location_name",
        "tabc_permit",
        "date",
        "total",
        "location",
    )
    readonly_fields = fields
    show_change_link = True


@admin.register(models.Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    ordering = ("name",)
    inlines = [ReceiptInline]


@admin.register(models.Location)
class LocationAdmin(GeoModelAdmin):
    list_display = ("name", "street_address", "city", "state", "zip")
    list_filter = ("coordinate_quality",)
    search_fields = ("name",)

    # Detail
    ########

    inlines = [
        ReceiptInline,
    ]
    save_on_top = True
    readonly_fields = ("street_address", "city", "state", "zip", "data")


@admin.register(models.Receipt)
class ReceiptAdmin(admin.ModelAdmin):
    list_display = ("location_name", "taxpayer_name", "date", "total")
    search_fields = ("location_name", "taxpayer_name")
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "taxpayer_name",
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
                    ("location_name", "location_number"),
                    "location_link",
                    "county_code",
                )
            },
        ),
        ("Relations", {"fields": ("business",)}),
    )
    readonly_fields = (
        "taxpayer_name",
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
        "location_link",
    )

    def location_link(self, obj):
        url = reverse("admin:receipts_location_change", args=(obj.location.pk,))
        return mark_safe(
            f'<a href="{url}">{obj.location}<br>{obj.location.address}</a>'
        )

    location_link.short_description = "location"  # type: ignore
