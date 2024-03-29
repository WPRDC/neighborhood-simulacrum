# Generated by Django 3.2 on 2022-08-29 02:14

import django.contrib.postgres.fields
from django.db import migrations, models
import markdownx.models


class Migration(migrations.Migration):

    dependencies = [
        ('context', '0006_auto_20220728_2055'),
        ('maps', '0006_rename_datalayer_indicatorlayer'),
    ]

    operations = [
        migrations.CreateModel(
            name='MapLayer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('slug', models.SlugField(max_length=128, unique=True)),
                ('description', models.TextField(blank=True, help_text='1 or 2 sentences', null=True, verbose_name='Short Description')),
                ('full_description', markdownx.models.MarkdownxField(blank=True, help_text='Full description with markdown functionality.', null=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('geog_type', models.CharField(choices=[('Point', 'Point'), ('LineString', 'LineString'), ('Polygon', 'Polygon'), ('MultiPoint', 'MultiPoint'), ('MultiLineString', 'MultiLineString'), ('MultiPolygon', 'MultiPolygon')], max_length=15)),
                ('source_override', models.JSONField()),
                ('layers_override', models.JSONField()),
                ('tags', models.ManyToManyField(blank=True, to='context.Tag')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CKANLayer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('slug', models.SlugField(max_length=128, unique=True)),
                ('description', models.TextField(blank=True, help_text='1 or 2 sentences', null=True, verbose_name='Short Description')),
                ('full_description', markdownx.models.MarkdownxField(blank=True, help_text='Full description with markdown functionality.', null=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('resource_id', models.UUIDField()),
                ('package_id', models.UUIDField()),
                ('geom_field', models.CharField(default='_geom', max_length=100)),
                ('id_field', models.CharField(default='_id', max_length=100)),
                ('extra_fields', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=100), default=list, size=None)),
                ('sql_override', models.TextField()),
                ('tags', models.ManyToManyField(blank=True, to='context.Tag')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
