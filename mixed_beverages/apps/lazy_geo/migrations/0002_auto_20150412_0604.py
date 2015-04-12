# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('lazy_geo', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='correction',
            name='approved_at',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='correction',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
