# Generated by Django 3.2 on 2022-07-22 00:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('indicators', '0024_auto_20220722_0001'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='timeaxis',
            name='time_parts',
        ),
    ]