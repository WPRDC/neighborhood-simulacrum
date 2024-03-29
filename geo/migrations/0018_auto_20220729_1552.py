# Generated by Django 3.2 on 2022-07-29 15:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('geo', '0017_auto_20220303_2053'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='adminregion',
            options={},
        ),
        migrations.AlterField(
            model_name='adminregion',
            name='global_geoid',
            field=models.CharField(blank=True, max_length=21, null=True, unique=True),
        ),
        migrations.AddIndex(
            model_name='adminregion',
            index=models.Index(fields=['global_geoid'], name='geo_adminre_global__a4a481_idx'),
        ),
    ]
