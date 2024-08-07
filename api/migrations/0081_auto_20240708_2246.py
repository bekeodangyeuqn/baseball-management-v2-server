# Generated by Django 3.2.20 on 2024-07-08 15:46

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0080_auto_20240629_1418'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='timeStart',
            field=models.DateTimeField(default=datetime.datetime(2024, 7, 8, 22, 45, 38, 829556)),
        ),
        migrations.AlterField(
            model_name='game',
            name='timeStart',
            field=models.DateTimeField(default=datetime.datetime(2024, 7, 8, 22, 45, 38, 834585)),
        ),
        migrations.AlterField(
            model_name='joinrequest',
            name='accepted',
            field=models.IntegerField(blank=True, choices=[(-1, 'False'), (0, 'Pending'), (1, 'True')], default=0, max_length=1),
        ),
        migrations.AlterField(
            model_name='notification',
            name='time',
            field=models.DateTimeField(default=datetime.datetime(2024, 7, 8, 22, 45, 38, 843156)),
        ),
    ]
