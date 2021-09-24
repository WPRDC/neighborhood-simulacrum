# Generated by Django 3.2.5 on 2021-08-26 19:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('indicators', '0035_auto_20210820_1303'),
    ]

    operations = [
        migrations.AlterField(
            model_name='variable',
            name='units',
            field=models.CharField(blank=True, help_text='Special format for $.  Otherwise, displayed after value.', max_length=30, null=True),
        ),
    ]