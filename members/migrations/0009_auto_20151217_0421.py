# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2015-12-17 04:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0008_auto_20151216_0502'),
    ]

    operations = [
        migrations.AddField(
            model_name='member',
            name='administrative_area_level_1',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='member',
            name='administrative_area_level_2',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='member',
            name='country',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='member',
            name='locality',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
