# Generated by Django 3.2.20 on 2024-03-31 08:12

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0060_auto_20240331_1511'),
    ]

    operations = [
        migrations.AddField(
            model_name='atbat',
            name='currentPitcher',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='current_pitcher', to='api.playergame'),
        ),
        migrations.AlterField(
            model_name='event',
            name='timeStart',
            field=models.DateTimeField(default=datetime.datetime(2024, 3, 31, 15, 12, 23, 429013)),
        ),
        migrations.AlterField(
            model_name='game',
            name='timeStart',
            field=models.DateTimeField(default=datetime.datetime(2024, 3, 31, 15, 12, 23, 431005)),
        ),
        migrations.AlterField(
            model_name='practice',
            name='timeStart',
            field=models.DateTimeField(default=datetime.datetime(2024, 3, 31, 15, 12, 23, 429013)),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='time',
            field=models.DateTimeField(default=datetime.datetime(2024, 3, 31, 15, 12, 23, 432016)),
        ),
    ]
