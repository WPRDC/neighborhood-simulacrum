# Generated by Django 3.2 on 2022-07-28 20:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('public_housing', '0013_auto_20220519_2102'),
    ]

    operations = [
        migrations.AlterField(
            model_name='watchlist',
            name='name',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='watchlist',
            name='slug',
            field=models.SlugField(max_length=64, unique=True),
        ),
    ]
