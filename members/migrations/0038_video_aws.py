# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-05-31 10:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0037_auto_20160530_1541'),
    ]

    operations = [
        migrations.AddField(
            model_name='video',
            name='aws',
            field=models.BooleanField(default=False),
        ),
    ]
