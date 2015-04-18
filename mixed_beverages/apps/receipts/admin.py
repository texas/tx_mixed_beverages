from django import forms
from django.contrib import admin
from django.contrib.gis.db.models.fields import PointField

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
    def display_name(self, obj):
        return obj.data['name']

    def display_tax(self, obj):
        return obj.data['avg_tax']

    formfield_overrides = {
        PointField: {
            'widget': forms.TextInput(attrs={'size': 80}),
        }
    }
    inlines = [ReceiptInline, ]
    list_display = ('display_name', 'display_tax', 'coordinate_quality')
    list_filter = ('coordinate_quality', )
    save_on_top = True


@admin.register(models.Receipt)
class ReceiptAdmin(admin.ModelAdmin):
    list_display = ('name', 'date', 'tax', 'city', 'zip')
    search_fields = ('name', )
    readonly_fields = ('name', 'tabc_permit', 'date', 'tax', 'address', 'city',
        'state', 'zip', 'county_code', 'business', 'location')
