# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-03-25 16:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pro', '0030_auto_20160325_1525'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jobquestion',
            name='question',
            field=models.CharField(max_length=250, null=True),
        ),
    ]
