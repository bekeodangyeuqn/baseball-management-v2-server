# Generated by Django 3.2.20 on 2024-04-22 04:27

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('api', '0066_auto_20240418_2101'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='timeStart',
            field=models.DateTimeField(default=datetime.datetime(2024, 4, 22, 11, 27, 50, 78219)),
        ),
        migrations.AlterField(
            model_name='game',
            name='timeStart',
            field=models.DateTimeField(default=datetime.datetime(2024, 4, 22, 11, 27, 50, 81219)),
        ),
        migrations.AlterField(
            model_name='player',
            name='status',
            field=models.IntegerField(blank=True, choices=[(-1, 'Quited'), (0, 'Inactive'), (1, 'Active')], default=1, null=True),
        ),
        migrations.AlterField(
            model_name='practice',
            name='timeStart',
            field=models.DateTimeField(default=datetime.datetime(2024, 4, 22, 11, 27, 50, 79219)),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='time',
            field=models.DateTimeField(default=datetime.datetime(2024, 4, 22, 11, 27, 50, 83219)),
        ),
        migrations.CreateModel(
            name='UserPushToken',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('push_token', models.TextField(blank=True, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
