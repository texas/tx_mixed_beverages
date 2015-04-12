# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('receipts', '0004_auto_20150404_0215'),
    ]

    operations = [
        migrations.AlterField(
            model_name='location',
            name='coordinate_quality',
            field=models.CharField(blank=True, max_length=2, null=True, choices=[('me', 'User Inputted'), ('00', 'AddressPoint'), ('01', 'GPS'), ('02', 'Parcel'), ('03', 'StreetSegmentInterpolation'), ('09', 'AddressZipCentroid'), ('10', 'POBoxZIPCentroid'), ('11', 'CityCentroid'), ('98', 'Unknown'), ('99', 'Unmatchable')]),
        ),
    ]
