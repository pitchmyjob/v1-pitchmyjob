# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-05-30 15:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pro', '0041_auto_20160530_1541'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pro',
            name='mp_broadbean_id',
        ),
        migrations.RemoveField(
            model_name='pro',
            name='mp_broadbean_ref',
        ),
        migrations.AddField(
            model_name='job',
            name='mp_broadbean_id',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='job',
            name='mp_broadbean_ref',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
