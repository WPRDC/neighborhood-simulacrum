# Generated by Django 3.1.7 on 2021-04-05 17:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('indicators', '0017_auto_20210330_2315'),
    ]

    operations = [
        migrations.AddField(
            model_name='ckanregionalsource',
            name='zipcode_field',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Zip code field'),
        ),
        migrations.AddField(
            model_name='ckanregionalsource',
            name='zipcode_field_is_sql',
            field=models.BooleanField(default=False),
        ),
    ]
