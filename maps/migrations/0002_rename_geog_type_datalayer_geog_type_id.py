# Generated by Django 3.2.7 on 2021-11-03 21:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('maps', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='datalayer',
            old_name='geog_type',
            new_name='geog_type_id',
        ),
    ]
