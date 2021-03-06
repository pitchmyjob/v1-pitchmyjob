# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-01-10 16:09
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0002_auto_20160110_1503'),
    ]

    operations = [
        migrations.AlterField(
            model_name='block',
            name='blocked',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='blocked', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='block',
            name='blocker',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='blocking', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='message',
            name='receiver',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='message_received', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='message',
            name='sender',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='message_sent', to=settings.AUTH_USER_MODEL),
        ),
    ]
