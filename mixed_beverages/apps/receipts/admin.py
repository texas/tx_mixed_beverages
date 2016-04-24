from django.contrib import admin
from django.contrib.gis.admin import GeoModelAdmin

from . import models


class ReceiptInline(admin.TabularInline):
    extra = 0
    model = models.Receipt
    readonly_fields = (
        'name', 'tabc_permit', 'date', 'tax', 'address', 'city',
        'state', 'zip', 'county_code', 'business', 'location',
    )


@admin.register(models.Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = ('name', )
    search_fields = ('name', )
    ordering = ('name', )
    inlines = [ReceiptInline]


@admin.register(models.Location)
class LocationAdmin(GeoModelAdmin):
    # List
    ######

    def display_name(self, obj):
        return obj.data['name']

    def display_tax(self, obj):
        return obj.data['avg_tax']

    list_display = ('display_name', 'display_tax', 'coordinate_quality')
    list_filter = ('coordinate_quality', )

    # Detail
    ########

    inlines = [ReceiptInline, ]
    save_on_top = True


@admin.register(models.Receipt)
class ReceiptAdmin(admin.ModelAdmin):
    list_display = ('name', 'date', 'tax', 'city', 'zip')
    search_fields = ('name', )
    readonly_fields = (
        'name', 'tabc_permit', 'date', 'tax', 'address', 'city',
        'state', 'zip', 'county_code', 'business', 'location',
    )
