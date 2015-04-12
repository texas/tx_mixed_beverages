# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('receipts', '0005_auto_20150412_0509'),
    ]

    operations = [
        migrations.CreateModel(
            name='Correction',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('fro', django.contrib.gis.db.models.fields.PointField(help_text='The old coordinate', srid=4326)),
                ('to', django.contrib.gis.db.models.fields.PointField(help_text='The suggested coordinate', srid=4326)),
                ('approved', models.BooleanField(default=False)),
                ('approved_by', models.ForeignKey(related_name='+', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('obj', models.ForeignKey(to='receipts.Location')),
                ('submitter', models.ForeignKey(related_name='+', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
    ]
