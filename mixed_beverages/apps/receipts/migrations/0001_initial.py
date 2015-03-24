# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Business',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='Receipt',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('permit', models.CharField(max_length=8)),
                ('name', models.CharField(max_length=30)),
                ('date', models.DateField(help_text='Use the 1st of the month for simplicity')),
                ('tax', models.DecimalField(max_digits=13, decimal_places=2)),
                ('address', models.CharField(max_length=30)),
                ('city', models.CharField(max_length=20)),
                ('state', models.CharField(max_length=2)),
                ('zip', models.CharField(max_length=5)),
                ('county_code', models.PositiveSmallIntegerField()),
                ('coordinate', django.contrib.gis.db.models.fields.PointField(srid=4326, null=True, blank=True)),
                ('business', models.ForeignKey(blank=True, to='receipts.Business', null=True)),
            ],
        ),
    ]
