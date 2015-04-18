from django.contrib import admin

from . import models


@admin.register(models.Correction)
class CorrectionAdmin(admin.ModelAdmin):
    list_display = ('obj', 'status', 'submitter', 'approved_by',
        'created_at', 'approved_at')
    list_filter = ('status', )
    raw_id_fields = ('obj', )
    readonly_fields = ('fro', 'to', 'submitter', 'approved_by', 'obj',
        'created_at', 'approved_at', 'ip_address')
