# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2015-12-17 00:05
from __future__ import unicode_literals

from django.db import migrations
import easy_thumbnails.fields
import pro.models


class Migration(migrations.Migration):

    dependencies = [
        ('pro', '0003_auto_20151212_0225'),
    ]

    operations = [
        migrations.AddField(
            model_name='pro',
            name='cover',
            field=easy_thumbnails.fields.ThumbnailerImageField(blank=True, default='pro/default.jpg', upload_to=pro.models.cover_filename),
        ),
    ]
