# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-03-04 23:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pro', '0022_pro_credit_job'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pro',
            name='credit_job',
            field=models.IntegerField(default=5),
        ),
    ]
