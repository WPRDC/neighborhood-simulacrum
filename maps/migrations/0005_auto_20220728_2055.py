# Generated by Django 3.2 on 2022-07-28 20:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maps', '0004_auto_20220728_2037'),
    ]

    operations = [
        migrations.AlterField(
            model_name='datalayer',
            name='name',
            field=models.CharField(max_length=200),
        ),
        migrations.AlterField(
            model_name='datalayer',
            name='slug',
            field=models.SlugField(max_length=128, unique=True),
        ),
    ]
