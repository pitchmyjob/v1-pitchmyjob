# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2015-12-12 02:22
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import easy_thumbnails.fields
import myc2v.mixins
import pro.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ActivityArea',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, null=True)),
                ('active', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name': "Secteur d'activit\xe9",
                'verbose_name_plural': "Liste des secteur d'activit\xe9",
            },
            bases=(myc2v.mixins.UnicodeNameMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Contract',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, null=True)),
                ('active', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name': 'Type de contrat',
                'verbose_name_plural': 'liste des type de contrat',
            },
            bases=(myc2v.mixins.UnicodeNameMixin, models.Model),
        ),
        migrations.CreateModel(
            name='ContractTime',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, null=True)),
                ('active', models.BooleanField(default=True)),
            ],
            bases=(myc2v.mixins.UnicodeNameMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Employes',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, null=True)),
                ('active', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name': "Nombre d'employ\xe9s",
                'verbose_name_plural': 'Liste nombre employ\xe9s',
            },
            bases=(myc2v.mixins.UnicodeNameMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company', models.CharField(max_length=200, null=True)),
                ('job_title', models.CharField(max_length=200, null=True)),
                ('contact', models.CharField(max_length=200, null=True)),
                ('job_location', models.CharField(max_length=200, null=True)),
                ('web_site', models.CharField(max_length=200, null=True)),
                ('salary_start', models.DecimalField(blank=True, decimal_places=2, max_digits=9, null=True)),
                ('salary_end', models.DecimalField(blank=True, decimal_places=2, max_digits=9, null=True)),
                ('description', models.TextField(null=True)),
                ('mission', models.TextField(blank=True, null=True)),
                ('profile', models.TextField(blank=True, null=True)),
                ('is_video', models.BooleanField(default=False)),
                ('is_audio', models.BooleanField(default=False)),
                ('is_text', models.BooleanField(default=False)),
                ('complet', models.BooleanField(default=False)),
                ('active', models.BooleanField(default=False)),
                ('date_created', models.DateField(auto_now_add=True, null=True)),
                ('last_update', models.DateTimeField(auto_now=True, null=True)),
                ('image', easy_thumbnails.fields.ThumbnailerImageField(blank=True, upload_to='job/')),
                ('activity_area', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='pro.ActivityArea')),
                ('contract_time', models.ManyToManyField(to='pro.ContractTime')),
                ('contracts', models.ManyToManyField(to='pro.Contract')),
            ],
        ),
        migrations.CreateModel(
            name='JobList',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, null=True)),
                ('active', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name': 'Metier',
                'verbose_name_plural': 'liste des metiers',
            },
            bases=(myc2v.mixins.UnicodeNameMixin, models.Model),
        ),
        migrations.CreateModel(
            name='JobQuestion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.CharField(max_length=200, null=True)),
                ('nb', models.IntegerField(null=True)),
                ('job', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='questions', to='pro.Job')),
            ],
        ),
        migrations.CreateModel(
            name='Pro',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company', models.CharField(max_length=150, null=True)),
                ('phone', models.CharField(max_length=150, null=True)),
                ('first_name', models.CharField(max_length=100, null=True)),
                ('last_name', models.CharField(max_length=100, null=True)),
                ('email', models.CharField(max_length=150, null=True)),
                ('web_site', models.CharField(blank=True, max_length=150, null=True)),
                ('headquarters', models.CharField(blank=True, max_length=150, null=True)),
                ('ca', models.CharField(max_length=150, null=True)),
                ('video_url', models.CharField(blank=True, max_length=200, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('image', easy_thumbnails.fields.ThumbnailerImageField(blank=True, default='pro/default.jpg', upload_to=pro.models.generate_filename)),
                ('activity_area', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='pro.ActivityArea')),
                ('employes', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='pro.Employes')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, null=True)),
            ],
            bases=(myc2v.mixins.UnicodeNameMixin, models.Model),
        ),
        migrations.AddField(
            model_name='job',
            name='pro',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='pro.Pro'),
        ),
        migrations.AddField(
            model_name='job',
            name='tags',
            field=models.ManyToManyField(to='pro.Tag'),
        ),
    ]
