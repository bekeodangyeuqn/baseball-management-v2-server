from datetime import datetime
from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import AtBat, Event, Game, JoinRequest, League, Manager, Player, Team, Transaction, Equipment, PlayerGame
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
        token['userid'] = user.id
        try:
            Manager.objects.get(user=user)
            token['id'] = Manager.objects.get(user=user).pk
            if Manager.objects.get(user=user).team != None:
                token['teamName'] = Manager.objects.get(user=user).team.name
                token['teamid'] = Manager.objects.get(user=user).team.pk
                token['shortName'] = Manager.objects.get(user=user).team.shortName
        except Manager.DoesNotExist:
            token['id'] = None
            token['teamName'] = None
            token['teamid'] = None
            token['shortName'] = None
        return token


class CreateManagerSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField()
    id = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Manager
        fields = ('firstName', 'lastName', 'date_of_birth', 'avatar', 'avatar_str', 'user_id', 'id', 
                  'homeTown', 'jerseyNumber', 'phoneNumber', 'email'
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
                  'homeStadium', 'foundedDate', 'logo_str', 'logo', 'managers', 'user_id', 'id', 'teamFund')

    def get_managers(self, obj):
        query_set = Manager.objects.filter(team=obj)
        return [ManagerDetailSerializer(item).data for item in query_set]
    
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
    
class JoinRequestSerializer(serializers.ModelSerializer):
    manager_id = serializers.IntegerField()
    team_id = serializers.IntegerField()
    class Meta:
        model = JoinRequest
        fields = ('manager_id', 'team_id')

    def create(self, validated_data):
        join_request = JoinRequest.objects.create(manager_id=validated_data['manager_id'], team_id=validated_data['team_id'])
        join_request.save()
        return join_request
    
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

class ManagerDetailSerializer(serializers.ModelSerializer):
    team_id = serializers.IntegerField()
    id = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Manager
        fields = ('firstName', 'lastName', 'team_id',
                  'date_of_birth', 'homeTown', 'jerseyNumber', 'phoneNumber', 'avatar', 'avatar_str', 'email','id')
    
    def get_id(self, obj):
        return obj.id
    
    def create(self, validated_data):
        # avatar = base64_to_image(validated_data['avatar_str'])
        manager = Manager.objects.create(firstName=validated_data['firstName'], lastName=validated_data['lastName'], team_id=validated_data['team_id'], 
                                        date_of_birth=validated_data['date_of_birth'], homeTown=validated_data['homeTown'], jerseyNumber=validated_data['jerseyNumber'],
                                       phoneNumber = validated_data['phoneNumber'], email=validated_data['email'], 
        )
        manager.save()

        return manager
    
    
class PlayerAvatarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ('avatar_str',)
    
    
class PlayerListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ('firstName', 'lastName', 'jerseyNumber', 'firstPos', 'secondPos', 'avatar','id')

class ManagerListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manager
        fields = ('firstName', 'lastName', 'jerseyNumber', 'avatar','id')
    
class ImporterSerializer(serializers.Serializer):
    file = serializers.FileField()
    
class EventSerializer(serializers.ModelSerializer):
    team_id = serializers.IntegerField()
    id = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Event
        fields = ('title', 'description', 'team_id', 'location', 'timeStart', 'timeEnd', 'id', 'status')

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
    
class TransactionSerializer(serializers.ModelSerializer):
    team_id = serializers.IntegerField()
    id = serializers.SerializerMethodField(read_only=True)
    player_id = serializers.IntegerField()

    class Meta:
        model = Transaction
        fields = ('player_id', 'description', 'team_id', 'type', 'time', 'price', 'id')

    def get_id(self, obj):
        return obj.id
    
    def create(self,validated_data):
        transaction = Transaction.objects.create(player_id=validated_data['player_id'],description=validated_data['description'],team_id=validated_data['team_id'], 
                                     type=validated_data['type'], time=validated_data['time'], price=validated_data['price'])
        transaction.save()
        return transaction
    
class EquipmentSerializer(serializers.ModelSerializer):
    team_id = serializers.IntegerField()
    id = serializers.SerializerMethodField(read_only=True)
    player_id = serializers.IntegerField()

    class Meta:
        model = Equipment
        fields = ('player_id', 'team_id', 'name', 'category', 'brand', 'price', 'description','avatar', 'avatar_str', 'id')

    def get_id(self, obj):
        return obj.id
    
    def create(self,validated_data):
        avatar = base64_to_image(validated_data['avatar_str'])
        equipment = Equipment.objects.create(player_id=validated_data['player_id'],team_id=validated_data['team_id'], name=validated_data["name"],
                                     category=validated_data['category'], brand=validated_data['brand'], description=validated_data['description'], avatar=avatar)
        equipment.save()
        return equipment
    
class PlayerGameCreateSerializer(serializers.ModelSerializer):
    game_id = serializers.IntegerField()
    player_id = serializers.IntegerField()
    id = serializers.SerializerMethodField(read_only=True)
    # runner_first = serializers.Field(required=False)
    # runner_second = serializers.Field(required=False)
    # runner_third = serializers.Field(required=False)
    # current_pitcher = serializers.Field(required=False)
    # atBat = serializers.ReadOnlyField()
    # hit = serializers.ReadOnlyField() 
    # battingAverage = serializers.ReadOnlyField() 
    # onBasePercentage = serializers.ReadOnlyField() 
    # sluggingPercentage = serializers.ReadOnlyField()
    # onBasePlusSlugging = serializers.ReadOnlyField() 
    # weightedOnBasePercentage = serializers.ReadOnlyField() 
    # totalChance = serializers.ReadOnlyField()
    # fieldingPercentace = serializers.ReadOnlyField() 
    # earnedRunAvarage = serializers.ReadOnlyField() 
    # walkAndHitPerInning = serializers.ReadOnlyField() 
    # runnerAllowed = serializers.ReadOnlyField() 
    # battingAvarageAgainst = serializers.ReadOnlyField() 
    # firstPitchStrikePercenttage = serializers.ReadOnlyField() 
    # fieldingIndependentPitching = serializers.ReadOnlyField() 

    class Meta:
        model = PlayerGame
        fields = [f.name for f in PlayerGame._meta.get_fields() if f.name not in ['game', 'player', 'runner_first', 'runner_second', 'runner_third', 'current_pitcher']]
        fields += ['game_id', 'player_id', 'id']
        

    def get_id(self, obj):
        return obj.id

    def create(self,validated_data):
        playerGame = PlayerGame.objects.create(player_id=validated_data['player_id'],game_id=validated_data['game_id'], 
                                     plateApperance=validated_data['plateApperance'], runBattedIn=validated_data['runBattedIn'], single=validated_data['single'], 
                                     double=validated_data['double'], triple=validated_data['triple'], battingOrder=validated_data['battingOrder'],
                                     homeRun=validated_data['homeRun'], baseOnBall=validated_data['baseOnBall'], 
                                     intentionalBB=validated_data['intentionalBB'], hitByPitch=validated_data['hitByPitch'], 
                                     strikeOut=validated_data['strikeOut'], fielderChoice=validated_data['fielderChoice'], 
                                     sacrificeFly=validated_data['sacrificeFly'], sacrificeBunt=validated_data['sacrificeBunt'], 
                                     stolenBase=validated_data['stolenBase'], leftOnBase=validated_data['leftOnBase'],  doublePlay=validated_data['doublePlay'], 
                                     triplePlay=validated_data['triplePlay'], run = validated_data['run'], onBaseByError=validated_data['onBaseByError'],
                                     position=validated_data['position'], playedPos=validated_data['playedPos'], putOut=validated_data['putOut'], 
                                     assist=validated_data['assist'], error=validated_data['error'], pitchBall=validated_data['pitchBall'],
                                     pitchStrike=validated_data['pitchStrike'], totalBatterFaced=validated_data['totalBatterFaced'], totalInGameOut=validated_data['totalInGameOut'],
                                     oppHit=validated_data['oppHit'], oppRun=validated_data['oppRun'], earnedRun=validated_data['earnedRun'], oppBaseOnBall=validated_data['oppBaseOnBall'],
                                     oppStrikeOut=validated_data['oppStrikeOut'], hitBatter=validated_data['hitBatter'], balk=validated_data['balk'], wildPitch=validated_data['wildPitch'],
                                     oppHomeRun=validated_data['oppHomeRun'], firstPitchStrike=validated_data['firstPitchStrike'], pickOff=validated_data['pickOff'],)
        playerGame.save()
        return playerGame
    
class PlayerGameSerializer(serializers.ModelSerializer):
    game_id = serializers.IntegerField()
    player_id = serializers.IntegerField()
    id = serializers.SerializerMethodField(read_only=True)
    atBat = serializers.ReadOnlyField()
    hit = serializers.ReadOnlyField() 
    battingAverage = serializers.ReadOnlyField() 
    onBasePercentage = serializers.ReadOnlyField() 
    sluggingPercentage = serializers.ReadOnlyField()
    onBasePlusSlugging = serializers.ReadOnlyField() 
    weightedOnBasePercentage = serializers.ReadOnlyField() 
    totalChance = serializers.ReadOnlyField()
    fieldingPercentace = serializers.ReadOnlyField() 
    earnedRunAvarage = serializers.ReadOnlyField() 
    walkAndHitPerInning = serializers.ReadOnlyField() 
    runnerAllowed = serializers.ReadOnlyField() 
    battingAvarageAgainst = serializers.ReadOnlyField() 
    firstPitchStrikePercenttage = serializers.ReadOnlyField() 
    fieldingIndependentPitching = serializers.ReadOnlyField() 

    class Meta:
        model = PlayerGame
        fields = '__all__'
    def get_id(self, obj):
        return obj.id
    
class AtBatSerializer(serializers.ModelSerializer):
    game_id = serializers.IntegerField()
    isRunnerFirstOff_id = serializers.IntegerField()
    isRunnerSecondOff_id = serializers.IntegerField()
    isRunnerThirdOff_id = serializers.IntegerField()
    currentPitcher_id = serializers.IntegerField()

    class Meta:
        model = AtBat
        fields = '__all__'

    def get_id(self, obj):
        return obj.id
    
    def create(self,validated_data):
        atBat = AtBat.objects.create(game_id=validated_data['game_id'], isRunnerFirstOff_id=validated_data['isRunnerFirstOff_id'],
                                     isRunnerSecondOff_id=validated_data['isRunnerSecondOff_id'], isRunnerThirdOff_id=validated_data['isRunnerThirdOff_id'], 
                                     inning=validated_data['inning'], out=validated_data['out'], ball=validated_data['ball'], strike=validated_data['strike'], 
                                     teamScore=validated_data['teamScore'], oppScore=validated_data['oppScore'], isTop=validated_data['isTop'], 
                                     isOffense=validated_data['isOffense'], isRunnerFirstDef=validated_data['isRunnerFirstDef'], isRunnerSecondDef=validated_data['isRunnerSecondDef'], 
                                     isRunnerThirdDef=validated_data['isRunnerThirdDef'], currentPitcher_id=validated_data['currentPitcher_id'], 
                                     oppCurPlayer=validated_data['oppCurPlayer'], currentPlayer=validated_data['currentPlayer'], 
                                     outcomeType=validated_data['outcomeType'], description=validated_data['description'])
        atBat.save()
        return atBat


