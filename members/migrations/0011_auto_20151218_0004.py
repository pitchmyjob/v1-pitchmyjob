# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2015-12-18 00:04
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0010_candidature_candidaturereponse'),
    ]

    operations = [
        migrations.AlterField(
            model_name='candidature',
            name='job',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='pro.Job'),
        ),
        migrations.AlterField(
            model_name='candidature',
            name='member',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='members.Member'),
        ),
    ]
