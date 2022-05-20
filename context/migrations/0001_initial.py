# Generated by Django 3.2 on 2022-05-19 21:02

from django.db import migrations, models
import django.db.models.deletion
import markdownx.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Link',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('slug', models.SlugField(max_length=200, unique=True)),
                ('url', models.URLField()),
                ('text', models.CharField(blank=True, help_text='leave blank to use "Name"', max_length=255, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('slug', models.SlugField(max_length=200, unique=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ContextItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('slug', models.SlugField(max_length=200, unique=True)),
                ('level', models.CharField(choices=[('_', 'Default (plain)'), ('I', 'Info (about the data)'), ('N', 'Note (about our process)'), ('W', 'Warning (w/ ⚠'), ('E', 'Error (with source data)')], max_length=2)),
                ('text', markdownx.models.MarkdownxField(help_text='Markdown enabled!')),
                ('link', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='context.link', verbose_name='Primary Link')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
