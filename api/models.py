from django.db import models

# Create your models here.
from django.contrib.auth.models import User


class Team(models.Model):
    name = models.CharField(max_length=200)
    shortName = models.CharField(max_length=4)
    city = models.CharField(max_length=200, blank=True, null=True)
    country = models.CharField(max_length=200, blank=True, null=True)
    homeStadium = models.CharField(max_length=500, blank=True, null=True)
    foundedDate = models.DateField(null=True, blank=True)
    logo = models.ImageField(
        upload_to="logos/", default="logos/logo.png", null=True, blank=True)
    logo_str = models.TextField(blank=True, null=True)
    user_id = models.IntegerField(blank=True, null=True)


class Manager(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date_of_birth = models.DateField(
        help_text="Date of birth", blank=True, null=True)
    avatar = models.ImageField(
        upload_to="avatars/", default="avatars/avatar.png", blank=True, null=True)
    avatar_str = models.TextField(blank=True, null=True)
    team = models.ForeignKey(
        Team, on_delete=models.CASCADE, blank=True, null=True)
    firstName = models.CharField(max_length=30, blank=True)
    lastName = models.CharField(max_length=30, blank=True)
