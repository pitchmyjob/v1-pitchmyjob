# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-01-11 06:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0005_message_view'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='date_posted',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]
