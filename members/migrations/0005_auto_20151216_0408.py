# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2015-12-16 04:08
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0004_video'),
    ]

    operations = [
        migrations.AlterField(
            model_name='video',
            name='embed_url',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
        migrations.AlterField(
            model_name='video',
            name='file_on_server',
            field=models.FileField(blank=True, null=True, upload_to='videos'),
        ),
        migrations.AlterField(
            model_name='video',
            name='link_url',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
        migrations.AlterField(
            model_name='video',
            name='member',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='members.Member'),
        ),
        migrations.AlterField(
            model_name='video',
            name='type_video',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='video',
            name='video_id',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
    ]
