# Generated by Django 3.2.20 on 2023-11-14 08:27

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0013_auto_20231114_1525'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='timeStart',
            field=models.DateTimeField(default=datetime.datetime(2023, 11, 14, 15, 27, 34, 540462)),
        ),
        migrations.AlterField(
            model_name='game',
            name='timeStart',
            field=models.DateTimeField(default=datetime.datetime(2023, 11, 14, 15, 27, 34, 542462)),
        ),
    ]
