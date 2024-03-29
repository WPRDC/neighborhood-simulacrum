# Generated by Django 3.2 on 2022-06-10 15:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('indicators', '0019_auto_20220526_2219'),
    ]

    operations = [
        migrations.CreateModel(
            name='DomainTopic',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.IntegerField(default=0)),
                ('domain', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='domain_to_topic', to='indicators.domain')),
                ('topic', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='topic_to_domain', to='indicators.topic')),
            ],
            options={
                'ordering': ('order',),
                'unique_together': {('domain', 'topic')},
            },
        ),
        migrations.AddField(
            model_name='domain',
            name='topics',
            field=models.ManyToManyField(related_name='domains', through='indicators.DomainTopic', to='indicators.Topic'),
        ),
    ]
