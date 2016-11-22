# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-11-22 16:57
from __future__ import unicode_literals

from django.db import migrations, models
import members.models


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0046_auto_20161111_0152'),
    ]

    operations = [
        migrations.AlterField(
            model_name='member',
            name='birthday',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='member',
            name='cv_pdf',
            field=models.FileField(blank=True, null=True, upload_to=members.models.generate_filename),
        ),
    ]
