# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-04-19 17:42
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0007_apec_region'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='apec',
            options={'ordering': ['-publication']},
        ),
        migrations.AddField(
            model_name='apec',
            name='sent',
            field=models.BooleanField(default=False),
        ),
    ]
