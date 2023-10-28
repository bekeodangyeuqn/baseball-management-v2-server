from datetime import datetime
from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import Manager, Team
import base64
from django.core.files.base import ContentFile
import string
import random

# initializing size of string
N = 16


def base64_to_image(base64_string):
    format, imgstr = base64_string.split(';base64,')
    ext = format.split('/')[-1]
    res = ''.join(random.choices(string.ascii_lowercase +
                                 string.digits, k=N))
    return ContentFile(base64.b64decode(imgstr), name=str(res) + "." + ext)


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    username = serializers.CharField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(write_only=True, required=True, style={
                                     'input_type': 'password'})
    confirmPassword = serializers.CharField(write_only=True, required=True, style={
                                            'input_type': 'confirmPassword'})

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'confirmPassword']

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):
        token = super(MyTokenObtainPairSerializer, cls).get_token(user)

        # Add custom claims
        token['username'] = user.username
        token['id'] = user.id
        # token['manageer'] = Manager.objects.get(id=user.id)
        return token


class ManagerSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField()

    class Meta:
        model = Manager
        fields = ('firstName', 'lastName', 'date_of_birth', 'avatar', 'avatar_str', 'user_id'
                  )

    def create(self, validated_data):
        avatar = base64_to_image(validated_data['avatar_str'])
        # date_of_birth = datetime.strptime(
        #     validated_data['date_of_birth'], '%m/%d/%y')
        manager = Manager.objects.create(
            firstName=validated_data['firstName'], lastName=validated_data['lastName'], date_of_birth=validated_data['date_of_birth'], avatar=avatar, user_id=validated_data['user_id'])
        manager.save()
        return manager


class TeamSerializer(serializers.ModelSerializer):
    managers = serializers.SerializerMethodField()
    user_id = serializers.IntegerField()

    class Meta:
        model = Team
        fields = ('name', 'shortName', 'city', 'country',
                  'homeStadium', 'foundedDate', 'logo_str', 'logo', 'managers', 'user_id')

    def get_managers(self, obj):
        query_set = Manager.objects.filter(team=obj)
        return [ManagerSerializer(item).data for item in query_set]

    def create(self, validated_data):
        logo = base64_to_image(validated_data['logo_str'])
        # date_of_birth = datetime.strptime(
        #     validated_data['date_of_birth'], '%m/%d/%y')
        team = Team.objects.create(
            name=validated_data['name'], shortName=validated_data['shortName'], country=validated_data['country'], city=validated_data['city'], homeStadium=validated_data['homeStadium'], foundedDate=validated_data['foundedDate'], logo=logo)
        team.save()
        manager = Manager.objects.get(user_id=validated_data['user_id'])
        manager.team = team
        manager.save()
        return team
