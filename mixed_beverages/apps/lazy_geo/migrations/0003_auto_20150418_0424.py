# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lazy_geo', '0002_auto_20150412_0604'),
    ]

    operations = [
        migrations.AddField(
            model_name='correction',
            name='comment',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='correction',
            name='ip_address',
            field=models.GenericIPAddressField(unpack_ipv4=True, null=True, verbose_name='IP address', blank=True),
        ),
        migrations.AddField(
            model_name='correction',
            name='status',
            field=models.CharField(default='approved', max_length=20, choices=[('submitted', 'Submitted'), ('approved', 'Approved'), ('rejected', 'Rejected')]),
            preserve_default=False,
        ),
    ]
