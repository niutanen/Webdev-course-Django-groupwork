# Generated by Django 2.1.3 on 2019-02-19 15:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gameshop', '0003_auto_20190219_1650'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='games',
            name='highscore',
        ),
        migrations.RemoveField(
            model_name='gamestate',
            name='score',
        ),
    ]
