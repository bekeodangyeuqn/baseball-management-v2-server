# Generated by Django 3.2.20 on 2024-06-03 04:51

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0077_auto_20240522_1608'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='managers',
            field=models.ManyToManyField(through='api.ManagerEvent', to='api.Manager'),
        ),
        migrations.AddField(
            model_name='event',
            name='players',
            field=models.ManyToManyField(through='api.PlayerEvent', to='api.Player'),
        ),
        migrations.AlterField(
            model_name='event',
            name='timeStart',
            field=models.DateTimeField(default=datetime.datetime(2024, 6, 3, 11, 51, 38, 215327)),
        ),
        migrations.AlterField(
            model_name='game',
            name='timeStart',
            field=models.DateTimeField(default=datetime.datetime(2024, 6, 3, 11, 51, 38, 215327)),
        ),
        migrations.AlterField(
            model_name='notification',
            name='time',
            field=models.DateTimeField(default=datetime.datetime(2024, 6, 3, 11, 51, 38, 215327)),
        ),
        migrations.AlterField(
            model_name='practice',
            name='timeStart',
            field=models.DateTimeField(default=datetime.datetime(2024, 6, 3, 11, 51, 38, 215327)),
        ),
    ]
