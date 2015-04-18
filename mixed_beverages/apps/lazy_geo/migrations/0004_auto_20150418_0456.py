# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lazy_geo', '0003_auto_20150418_0424'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='correction',
            name='approved',
        ),
        migrations.AlterField(
            model_name='correction',
            name='status',
            field=models.CharField(default='submitted', max_length=20, choices=[('submitted', 'Submitted'), ('approved', 'Approved'), ('rejected', 'Rejected')]),
        ),
    ]
