# Generated by Django 2.1.3 on 2019-02-19 14:35

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gameshop', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='games',
            name='highscore',
            field=django.contrib.postgres.fields.jsonb.JSONField(default='{}', null=True),
        ),
        migrations.AlterField(
            model_name='gamestate',
            name='score',
            field=django.contrib.postgres.fields.jsonb.JSONField(default='{}'),
        ),
    ]
