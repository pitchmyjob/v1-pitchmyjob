# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-03-29 15:56
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('factures', '0009_auto_20160329_1536'),
    ]

    operations = [
        migrations.AlterField(
            model_name='facture',
            name='prix_ht',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=8),
        ),
        migrations.AlterField(
            model_name='facture',
            name='prix_ttc',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=8),
        ),
        migrations.AlterField(
            model_name='facture',
            name='tva',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=8),
        ),
        migrations.AlterField(
            model_name='paymentlink',
            name='prix_ht',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=8),
        ),
    ]
