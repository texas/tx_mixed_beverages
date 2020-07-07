# Generated by Django 3.0.8 on 2020-07-05 07:48

import django.contrib.gis.db.models.fields
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Business",
            fields=[
                ("name", models.CharField(max_length=100)),
                (
                    "tax_number",
                    models.CharField(max_length=50, primary_key=True, serialize=False),
                ),
            ],
            options={"verbose_name_plural": "businesses",},
        ),
        migrations.CreateModel(
            name="Location",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "coordinate",
                    django.contrib.gis.db.models.fields.PointField(
                        blank=True, null=True, srid=4326
                    ),
                ),
                (
                    "coordinate_quality",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("me", "User Inputted"),
                            ("00", "AddressPoint"),
                            ("01", "GPS"),
                            ("02", "Parcel"),
                            ("03", "StreetSegmentInterpolation"),
                            ("09", "AddressZipCentroid"),
                            ("10", "POBoxZIPCentroid"),
                            ("11", "CityCentroid"),
                            ("98", "Unknown"),
                            ("99", "Unmatchable"),
                        ],
                        max_length=2,
                        null=True,
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        help_text="Location name from one of the receipts",
                        max_length=100,
                    ),
                ),
                ("street_address", models.CharField(max_length=100)),
                ("city", models.CharField(max_length=30)),
                ("state", models.CharField(max_length=20)),
                ("zip", models.CharField(max_length=15)),
                (
                    "data",
                    django.contrib.postgres.fields.jsonb.JSONField(
                        blank=True,
                        help_text="denormalized data to help generate map data",
                        null=True,
                    ),
                ),
            ],
            options={"abstract": False,},
        ),
        migrations.CreateModel(
            name="Receipt",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("taxpayer_name", models.CharField(max_length=100)),
                (
                    "tax_number",
                    models.CharField(max_length=80, verbose_name="taxpayer number"),
                ),
                (
                    "tabc_permit",
                    models.CharField(
                        help_text="example: MB888888",
                        max_length=40,
                        verbose_name="TABC permit number",
                    ),
                ),
                ("date", models.DateField(help_text="Obligation End Date")),
                (
                    "liquor",
                    models.DecimalField(
                        decimal_places=2, max_digits=13, verbose_name="liquor receipts"
                    ),
                ),
                (
                    "wine",
                    models.DecimalField(
                        decimal_places=2, max_digits=13, verbose_name="wine receipts"
                    ),
                ),
                (
                    "beer",
                    models.DecimalField(
                        decimal_places=2, max_digits=13, verbose_name="beer receipts"
                    ),
                ),
                (
                    "cover",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=13,
                        verbose_name="cover charge receipts",
                    ),
                ),
                (
                    "total",
                    models.DecimalField(
                        decimal_places=2, max_digits=13, verbose_name="total receipts"
                    ),
                ),
                ("location_name", models.CharField(max_length=100)),
                ("location_number", models.PositiveSmallIntegerField()),
                (
                    "county_code",
                    models.PositiveSmallIntegerField(
                        help_text="A number from 1 to 254"
                    ),
                ),
                (
                    "business",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="receipts",
                        to="receipts.Business",
                    ),
                ),
                (
                    "location",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="receipts",
                        to="receipts.Location",
                    ),
                ),
            ],
            options={
                "ordering": ("-date",),
                "unique_together": {("tabc_permit", "date")},
            },
        ),
    ]
