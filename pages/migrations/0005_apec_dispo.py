# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-04-18 22:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0004_apec'),
    ]

    operations = [
        migrations.AddField(
            model_name='apec',
            name='dispo',
            field=models.CharField(max_length=150, null=True),
        ),
    ]
