# Generated by Django 3.2.9 on 2022-01-13 20:20

from django.db import migrations, models
import markdownx.models


class Migration(migrations.Migration):

    dependencies = [
        ('maps', '0002_rename_geog_type_datalayer_geog_type_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='datalayer',
            name='full_description',
            field=markdownx.models.MarkdownxField(blank=True, help_text='Full description with markdown functionality.', null=True),
        ),
        migrations.AlterField(
            model_name='datalayer',
            name='description',
            field=models.TextField(blank=True, help_text='1 or 2 sentences', null=True, verbose_name='Short Description'),
        ),
    ]
