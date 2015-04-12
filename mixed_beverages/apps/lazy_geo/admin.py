from django import forms
from django.contrib import admin
from django.contrib.gis.db.models.fields import PointField

from . import models


@admin.register(models.Correction)
class CorrectionInline(admin.ModelAdmin):
    formfield_overrides = {
        PointField: {
            'widget': forms.TextInput(attrs={'size': 80}),
        }
    }
    raw_id_fields = ('obj', )
