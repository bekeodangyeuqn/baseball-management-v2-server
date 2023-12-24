from datetime import datetime
from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import Event, Game, League, Manager, Player, Team
import base64
from django.core.files.base import ContentFile
import string
import random

# initializing size of string
N = 24


def base64_to_image(base64_string):
    if (base64_string):
        format, imgstr = base64_string.split(';base64,')
        ext = format.split('/')[-1]
        res = ''.join(random.choices(string.ascii_lowercase +
                                    string.digits, k=N))
        return ContentFile(base64.b64decode(imgstr), name=str(res) + "." + ext)
    return None


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
        token['teamName'] = Manager.objects.get(user=user).team.name
        token['teamid'] = Manager.objects.get(user=user).team.pk
        return token


class ManagerSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField()
    id = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Manager
        fields = ('firstName', 'lastName', 'date_of_birth', 'avatar', 'avatar_str', 'user_id', 'id'
                  )
        
    def get_id(self, obj):
            return obj.id

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
    id = serializers.SerializerMethodField(read_only=True)
    user_id = serializers.IntegerField()

    class Meta:
        model = Team
        fields = ('name', 'shortName', 'city', 'country',
                  'homeStadium', 'foundedDate', 'logo_str', 'logo', 'managers', 'user_id', 'id')

    def get_managers(self, obj):
        query_set = Manager.objects.filter(team=obj)
        return [ManagerSerializer(item).data for item in query_set]
    
    def get_id(self, obj):
        return obj.id

    def create(self, validated_data):
        logo = base64_to_image(validated_data['logo_str'])
        # date_of_birth = datetime.strptime(
        #     validated_data['date_of_birth'], '%m/%d/%y')
        team = Team.objects.create(
            name=validated_data['name'], shortName=validated_data['shortName'], country=validated_data['country'], 
            city=validated_data['city'], homeStadium=validated_data['homeStadium'], foundedDate=validated_data['foundedDate'], logo=logo)
        team.save()
        manager = Manager.objects.get(user_id=validated_data['user_id'])
        manager.team = team
        manager.save()
        return team
    
class PlayerDetailSerializer(serializers.ModelSerializer):
    team_id = serializers.IntegerField()
    id = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Player
        fields = ('firstName', 'lastName', 'team_id', 'firstPos', 'secondPos', 'weight', 
                  'height', 'birthDate', 'homeTown', 'jerseyNumber', 'phoneNumber', 'avatar', 'avatar_str', 'email','id', 'batHand', 'throwHand')
    
    def get_id(self, obj):
        return obj.id
    
    def create(self, validated_data):
        # avatar = base64_to_image(validated_data['avatar_str'])
        player = Player.objects.create(firstName=validated_data['firstName'], lastName=validated_data['lastName'], team_id=validated_data['team_id'], 
                                       firstPos=validated_data['firstPos'], secondPos=validated_data['secondPos'], weight=validated_data['weight'], 
                                       height=validated_data['height'], birthDate=validated_data['birthDate'], homeTown=validated_data['homeTown'], jerseyNumber=validated_data['jerseyNumber'],
                                       phoneNumber = validated_data['phoneNumber'], email=validated_data['email'], 
                                       batHand=validated_data['batHand'], throwHand=validated_data['throwHand'])
        player.save()

        return player
    
    
class PlayerAvatarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ('avatar_str',)
    
    
class PlayerListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ('firstName', 'lastName', 'jerseyNumber', 'firstPos', 'secondPos', 'avatar','id')
    
class ImporterSerializer(serializers.Serializer):
    file = serializers.FileField()
    
class EventSerializer(serializers.ModelSerializer):
    team_id = serializers.IntegerField()
    id = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Event
        fields = ('title', 'description', 'team_id', 'location', 'timeStart', 'timeEnd', 'id')

    def get_id(self, obj):
        return obj.id
    
    def create(self,validated_data):
        event = Event.objects.create(title=validated_data['title'],description=validated_data['description'],team_id=validated_data['team_id'], 
                                     location=validated_data['location'], timeStart=validated_data['timeStart'], timeEnd=validated_data['timeEnd'])
        event.save()
        return event
    
class LeagueSerializer(serializers.ModelSerializer):
    team_id = serializers.IntegerField()
    id = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = League
        fields = ('title', 'description', 'team_id', 'location', 'timeStart', 'timeEnd', 'id', 'achieve')

    def get_id(self, obj):
        return obj.id
    
    def create(self,validated_data):
        league = League.objects.create(title=validated_data['title'],description=validated_data['description'],team_id=validated_data['team_id'], 
                                     location=validated_data['location'], timeStart=validated_data['timeStart'], timeEnd=validated_data['timeEnd'], achieve=validated_data['achieve'])
        league.save()
        return league
    
class GameCreateSerializer(serializers.ModelSerializer):
    team_id = serializers.IntegerField()
    league_id = serializers.IntegerField()
    id = serializers.SerializerMethodField(read_only=True)
    team_score = serializers.ReadOnlyField()
    team_hit = serializers.ReadOnlyField()
    team_error = serializers.ReadOnlyField()
    opp_score = serializers.ReadOnlyField()
    opp_hit = serializers.ReadOnlyField()
    opp_error = serializers.ReadOnlyField()

    class Meta:
        model = Game
        fields = '__all__'

    def get_id(self, obj):
        return obj.id
    
    def create(self,validated_data):
        game = Game.objects.create(oppTeam=validated_data['oppTeam'], oppTeamShort=validated_data['oppTeamShort'], description=validated_data['description'],team_id=validated_data['team_id'], 
                                     stadium=validated_data['stadium'], timeStart=validated_data['timeStart'], timeEnd=validated_data['timeEnd'], 
                                     league_id=validated_data['league_id'], inningERA=validated_data['inningERA'])
        game.save()
        return game
