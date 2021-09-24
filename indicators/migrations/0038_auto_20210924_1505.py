# Generated by Django 3.2.7 on 2021-09-24 15:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('indicators', '0037_auto_20210910_1714'),
    ]

    operations = [
        migrations.CreateModel(
            name='SubdomainIndicator',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.IntegerField(default=0)),
                ('indicator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='indicator_to_subdomain', to='indicators.indicator')),
                ('subdomain', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subdomain_to_indicator', to='indicators.subdomain')),
            ],
            options={
                'unique_together': {('subdomain', 'indicator')},
            },
        ),
        migrations.AddField(
            model_name='subdomain',
            name='inds',
            field=models.ManyToManyField(related_name='subdomains', through='indicators.SubdomainIndicator', to='indicators.Indicator'),
        ),
    ]