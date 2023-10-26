from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import Manager, Team


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
    class Meta:
        model = Manager
        fields = ('firstName', 'lastName', 'date_of_birth', 'avatar',
                  )


class TeamSerializer(serializers.ModelSerializer):
    manager_team = ManagerSerializer(many=True)

    class Meta:
        model = Team
        fields = ('name', 'shortName', 'city', 'country',
                  'homeStadium', 'foundedDate', 'logo')
