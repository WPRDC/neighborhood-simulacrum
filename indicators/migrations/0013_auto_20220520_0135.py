# Generated by Django 3.2 on 2022-05-20 01:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('context', '0002_contextitem_tags'),
        ('indicators', '0012_auto_20220304_1945'),
    ]

    operations = [
        migrations.AddField(
            model_name='dataviz',
            name='context',
            field=models.ManyToManyField(to='context.ContextItem'),
        ),
        migrations.AddField(
            model_name='dataviz',
            name='tags',
            field=models.ManyToManyField(to='context.Tag'),
        ),
        migrations.AddField(
            model_name='domain',
            name='context',
            field=models.ManyToManyField(to='context.ContextItem'),
        ),
        migrations.AddField(
            model_name='domain',
            name='tags',
            field=models.ManyToManyField(to='context.Tag'),
        ),
        migrations.AddField(
            model_name='indicator',
            name='context',
            field=models.ManyToManyField(to='context.ContextItem'),
        ),
        migrations.AddField(
            model_name='indicator',
            name='tags',
            field=models.ManyToManyField(to='context.Tag'),
        ),
        migrations.AddField(
            model_name='source',
            name='context',
            field=models.ManyToManyField(to='context.ContextItem'),
        ),
        migrations.AddField(
            model_name='source',
            name='tags',
            field=models.ManyToManyField(to='context.Tag'),
        ),
        migrations.AddField(
            model_name='subdomain',
            name='context',
            field=models.ManyToManyField(to='context.ContextItem'),
        ),
        migrations.AddField(
            model_name='subdomain',
            name='tags',
            field=models.ManyToManyField(to='context.Tag'),
        ),
        migrations.AddField(
            model_name='taxonomy',
            name='context',
            field=models.ManyToManyField(to='context.ContextItem'),
        ),
        migrations.AddField(
            model_name='taxonomy',
            name='tags',
            field=models.ManyToManyField(to='context.Tag'),
        ),
        migrations.AddField(
            model_name='timeaxis',
            name='context',
            field=models.ManyToManyField(to='context.ContextItem'),
        ),
        migrations.AddField(
            model_name='timeaxis',
            name='tags',
            field=models.ManyToManyField(to='context.Tag'),
        ),
        migrations.AddField(
            model_name='variable',
            name='context',
            field=models.ManyToManyField(to='context.ContextItem'),
        ),
        migrations.AddField(
            model_name='variable',
            name='tags',
            field=models.ManyToManyField(to='context.Tag'),
        ),
    ]
