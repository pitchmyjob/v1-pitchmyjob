# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-03-07 08:29
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0030_auto_20160304_1239'),
    ]

    operations = [
        migrations.AlterField(
            model_name='member',
            name='job_wanted',
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
    ]
