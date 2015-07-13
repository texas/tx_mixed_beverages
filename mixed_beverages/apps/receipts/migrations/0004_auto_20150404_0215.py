# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.postgres.fields.hstore
from django.contrib.postgres.operations import HStoreExtension


class Migration(migrations.Migration):

    dependencies = [
        ('receipts', '0003_auto_20150329_1812'),
    ]

    operations = [
        HStoreExtension(),
        migrations.AlterModelOptions(
            name='receipt',
            options={'ordering': ('-date',)},
        ),
        migrations.AddField(
            model_name='location',
            name='data',
            field=django.contrib.postgres.fields.hstore.HStoreField(null=True, blank=True),
        ),
    ]
