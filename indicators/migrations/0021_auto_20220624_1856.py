# Generated by Django 3.2 on 2022-06-24 18:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('indicators', '0020_auto_20220610_1519'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='subdomaintopic',
            unique_together=None,
        ),
        migrations.RemoveField(
            model_name='subdomaintopic',
            name='subdomain',
        ),
        migrations.RemoveField(
            model_name='subdomaintopic',
            name='topic',
        ),
        migrations.DeleteModel(
            name='Subdomain',
        ),
        migrations.DeleteModel(
            name='SubdomainTopic',
        ),
    ]
