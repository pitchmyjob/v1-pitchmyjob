# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-01-07 10:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0020_candidature_decline'),
    ]

    operations = [
        migrations.AddField(
            model_name='candidaturereponse',
            name='time',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
