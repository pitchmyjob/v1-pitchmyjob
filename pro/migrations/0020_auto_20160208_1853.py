# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-02-08 18:53
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pro', '0019_pro_view'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='jobquestion',
            options={'ordering': ['nb']},
        ),
    ]
