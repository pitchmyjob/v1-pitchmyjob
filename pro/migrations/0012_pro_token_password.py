# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2015-12-28 10:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pro', '0011_job_view'),
    ]

    operations = [
        migrations.AddField(
            model_name='pro',
            name='token_password',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
