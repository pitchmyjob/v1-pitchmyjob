# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-11-22 16:57
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0009_apec_vague'),
    ]

    operations = [
        migrations.CreateModel(
            name='LandingPage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(blank=True, max_length=250, null=True)),
                ('last_name', models.CharField(blank=True, max_length=250, null=True)),
                ('email', models.CharField(blank=True, max_length=250, null=True)),
                ('company', models.CharField(blank=True, max_length=250, null=True)),
                ('phone', models.CharField(blank=True, max_length=250, null=True)),
                ('fonction', models.CharField(blank=True, max_length=250, null=True)),
                ('employes', models.CharField(blank=True, max_length=250, null=True)),
                ('landing', models.CharField(blank=True, max_length=250, null=True)),
            ],
        ),
    ]
