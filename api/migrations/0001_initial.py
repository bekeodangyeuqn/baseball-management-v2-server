# Generated by Django 3.2.20 on 2023-10-26 14:51

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('shortName', models.CharField(max_length=4)),
                ('city', models.CharField(blank=True, max_length=200, null=True)),
                ('country', models.CharField(blank=True, max_length=200, null=True)),
                ('homeStadium', models.CharField(blank=True, max_length=500, null=True)),
                ('foundedDate', models.DateField(blank=True, null=True)),
                ('logo', models.ImageField(blank=True, default='logos/logo.png', null=True, upload_to='logos/')),
            ],
        ),
        migrations.CreateModel(
            name='Manager',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_of_birth', models.DateField(blank=True, help_text='Date of birth', null=True)),
                ('avatar', models.ImageField(blank=True, default='avatars/avatar.png', null=True, upload_to='avatars/')),
                ('team', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='api.team')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
