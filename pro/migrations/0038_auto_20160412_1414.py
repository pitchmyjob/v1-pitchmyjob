# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-04-12 14:14
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pro', '0037_seenjob'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='seenjob',
            options={'verbose_name': 'Job consult\xe9', 'verbose_name_plural': 'Liste des jobs consult\xe9s'},
        ),
        migrations.AlterField(
            model_name='job',
            name='contact',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
        migrations.AlterField(
            model_name='job',
            name='experiences',
            field=models.ManyToManyField(blank=True, to='members.Experience'),
        ),
        migrations.AlterField(
            model_name='job',
            name='studies',
            field=models.ManyToManyField(blank=True, to='members.Study'),
        ),
        migrations.AlterField(
            model_name='job',
            name='web_site',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
        migrations.AlterField(
            model_name='pro',
            name='credit_job',
            field=models.IntegerField(default=1),
        ),
    ]
