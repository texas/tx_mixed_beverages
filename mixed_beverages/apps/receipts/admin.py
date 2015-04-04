from django.contrib import admin

from . import models


class ReceiptInline(admin.TabularInline):
    extra = 0
    model = models.Receipt
    readonly_fields = ('name', 'tabc_permit', 'date', 'tax', 'address', 'city',
        'state', 'zip', 'county_code', 'business', 'location')


@admin.register(models.Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = ('name', )
    search_fields = ('name', )
    ordering = ('name', )
    inlines = [ReceiptInline, ]


@admin.register(models.Location)
class LocationAdmin(admin.ModelAdmin):
    inlines = [ReceiptInline, ]


@admin.register(models.Receipt)
class ReceiptAdmin(admin.ModelAdmin):
    list_display = ('name', 'date', 'tax', 'city', 'zip')
    search_fields = ('name', )
    readonly_fields = ('name', 'tabc_permit', 'date', 'tax', 'address', 'city',
        'state', 'zip', 'county_code', 'business', 'location')
