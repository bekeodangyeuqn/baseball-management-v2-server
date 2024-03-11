# Generated by Django 3.2.20 on 2024-03-11 04:20

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0043_auto_20240309_1149'),
    ]

    operations = [
        migrations.AlterField(
            model_name='equipment',
            name='price',
            field=models.BigIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='event',
            name='timeStart',
            field=models.DateTimeField(default=datetime.datetime(2024, 3, 11, 11, 20, 21, 769625)),
        ),
        migrations.AlterField(
            model_name='game',
            name='timeStart',
            field=models.DateTimeField(default=datetime.datetime(2024, 3, 11, 11, 20, 21, 769625)),
        ),
        migrations.AlterField(
            model_name='practice',
            name='timeStart',
            field=models.DateTimeField(default=datetime.datetime(2024, 3, 11, 11, 20, 21, 769625)),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='time',
            field=models.DateTimeField(default=datetime.datetime(2024, 3, 11, 11, 20, 21, 769625)),
        ),
    ]
