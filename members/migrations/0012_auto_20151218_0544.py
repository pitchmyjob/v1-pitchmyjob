# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2015-12-18 05:44
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0011_auto_20151218_0004'),
    ]

    operations = [
        migrations.AlterField(
            model_name='candidaturereponse',
            name='video',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='candidature', to='members.Video'),
        ),
    ]
