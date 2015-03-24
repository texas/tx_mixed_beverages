from django.contrib import admin

from . import models


@admin.register(models.Receipt)
class ReceiptAdmin(admin.ModelAdmin):
    list_display = ('name', 'date', 'tax', 'city', 'zip')
    search_fields = ('name', )
