# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-04-18 22:30
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0006_apec_publication'),
    ]

    operations = [
        migrations.AddField(
            model_name='apec',
            name='region',
            field=models.CharField(max_length=150, null=True),
        ),
    ]
