# Generated by Django 3.2 on 2022-05-20 15:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('context', '0003_alter_contextitem_link'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contextitem',
            name='level',
            field=models.CharField(choices=[('_', 'Default (plain)'), ('I', 'Info (about the data)'), ('N', 'Note (about our process)'), ('W', 'Warning (w/ ⚠)'), ('E', 'Error (with source data)')], max_length=2),
        ),
        migrations.AlterField(
            model_name='contextitem',
            name='tags',
            field=models.ManyToManyField(blank=True, to='context.Tag'),
        ),
    ]
