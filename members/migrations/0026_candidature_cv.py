# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-01-20 17:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0025_candidature_date_posted'),
    ]

    operations = [
        migrations.AddField(
            model_name='candidature',
            name='cv',
            field=models.FileField(blank=True, null=True, upload_to='candidatures/%Y/%m/'),
        ),
    ]
