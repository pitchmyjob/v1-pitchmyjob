# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-02-17 13:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('c2v', '0004_auto_20160208_2007'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cvexperience',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='cvformation',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
    ]
