# Generated by Django 3.2.20 on 2023-11-02 11:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_team_logo_str'),
    ]

    operations = [
        migrations.AddField(
            model_name='team',
            name='user_id',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
