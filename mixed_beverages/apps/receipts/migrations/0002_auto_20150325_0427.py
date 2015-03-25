# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('receipts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('coordinate', django.contrib.gis.db.models.fields.PointField(srid=4326, null=True, blank=True)),
            ],
        ),
        migrations.RenameField(
            model_name='receipt',
            old_name='permit',
            new_name='tabc_permit',
        ),
        migrations.RemoveField(
            model_name='receipt',
            name='coordinate',
        ),
        migrations.AlterField(
            model_name='receipt',
            name='business',
            field=models.ForeignKey(related_name='receipts', blank=True, to='receipts.Business', null=True),
        ),
        migrations.AddField(
            model_name='receipt',
            name='location',
            field=models.ForeignKey(related_name='receipts', blank=True, to='receipts.Location', null=True),
        ),
    ]
