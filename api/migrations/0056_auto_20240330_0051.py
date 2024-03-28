# Generated by Django 3.2.20 on 2024-03-29 17:51

import datetime
import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0055_auto_20240329_0252'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='timeStart',
            field=models.DateTimeField(default=datetime.datetime(2024, 3, 30, 0, 51, 29, 964379)),
        ),
        migrations.AlterField(
            model_name='game',
            name='timeStart',
            field=models.DateTimeField(default=datetime.datetime(2024, 3, 30, 0, 51, 29, 964379)),
        ),
        migrations.AlterField(
            model_name='playergame',
            name='playedPos',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(blank=True, choices=[(1, 'Picther'), (2, 'Catcher'), (3, 'First baseman'), (4, 'Second baseman'), (5, 'Third baseman'), (6, 'Shortstop'), (7, 'Left fielder'), (8, 'Center fielder'), (9, 'Right fielder'), (0, 'Desinated Hitter'), (-1, 'Not position')], default=-1), size=None),
        ),
        migrations.AlterField(
            model_name='playergame',
            name='position',
            field=models.IntegerField(blank=True, choices=[(1, 'Picther'), (2, 'Catcher'), (3, 'First baseman'), (4, 'Second baseman'), (5, 'Third baseman'), (6, 'Shortstop'), (7, 'Left fielder'), (8, 'Center fielder'), (9, 'Right fielder'), (0, 'Desinated Hitter'), (-1, 'Not position')], default=-1),
        ),
        migrations.AlterField(
            model_name='practice',
            name='timeStart',
            field=models.DateTimeField(default=datetime.datetime(2024, 3, 30, 0, 51, 29, 964379)),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='time',
            field=models.DateTimeField(default=datetime.datetime(2024, 3, 30, 0, 51, 29, 964379)),
        ),
    ]