# Generated by Django 3.2 on 2022-08-29 19:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maps', '0013_auto_20220829_1946'),
    ]

    operations = [
        migrations.AddField(
            model_name='ckanlayer',
            name='srid',
            field=models.IntegerField(default=4326),
        ),
    ]
