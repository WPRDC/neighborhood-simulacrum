# Generated by Django 3.2 on 2022-08-25 23:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('indicators', '0034_cachedindicatordata_indicators__expirat_f3b150_idx'),
        ('maps', '0005_auto_20220728_2055'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='DataLayer',
            new_name='IndicatorLayer',
        ),
    ]
