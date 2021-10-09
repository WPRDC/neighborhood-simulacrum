# Generated by Django 3.2.7 on 2021-10-09 16:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('census_data', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='censusvalue',
            name='census_table_uid',
            field=models.CharField(db_index=True, default='', max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='censusvalue',
            name='geog_uid',
            field=models.CharField(db_index=True, default='', max_length=100),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='censusvalue',
            unique_together={('geog_uid', 'census_table_uid')},
        ),
        migrations.AlterIndexTogether(
            name='censusvalue',
            index_together={('geog_uid', 'census_table_uid')},
        ),
        migrations.RemoveField(
            model_name='censusvalue',
            name='census_table',
        ),
        migrations.RemoveField(
            model_name='censusvalue',
            name='geography',
        ),
    ]
