# Generated by Django 3.2 on 2022-05-20 13:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('context', '0002_contextitem_tags'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contextitem',
            name='link',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='context.link', verbose_name='Primary Link'),
        ),
    ]
