# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-08-19 10:35
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pro', '0042_auto_20160530_1543'),
    ]

    operations = [
        migrations.AddField(
            model_name='pro',
            name='active',
            field=models.BooleanField(default=True),
        ),
    ]
