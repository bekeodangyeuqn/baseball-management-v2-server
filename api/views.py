from django.shortcuts import render
from rest_framework import status, generics
from rest_framework.response import Response
from django.contrib.auth.models import User
from .serializers import EventSerializer, GameCreateSerializer, ImporterSerializer, ManagerSerializer, PlayerAvatarSerializer, PlayerDetailSerializer, PlayerListSerializer, TeamSerializer, UserSerializer
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from django.contrib.auth import authenticate, login
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import permissions
from .serializers import MyTokenObtainPairSerializer
from .models import Event, Game, Manager, Player, Team
import pandas as pd
import numpy as np
import base64
from django.core.files.base import ContentFile
import string
import random

# initializing size of string
N = 24


def base64_to_image(base64_string):
    format, imgstr = base64_string.split(';base64,')
    ext = format.split('/')[-1]
    res = ''.join(random.choices(string.ascii_lowercase +
                                 string.digits, k=N))
    return ContentFile(base64.b64decode(imgstr), name=str(res) + "." + ext)

class UserCreate(APIView):
    permission_classes = (permissions.AllowAny,)
    authentication_classes = ()

    def post(self, request, format='json'):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            if user:
                json = serializer.data
                return Response(json, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLogin(APIView):
    permission_classes = (permissions.AllowAny,)
    authentication_classes = ()

    def post(self, request, format='json'):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=status.HTTP_200_OK)
        return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


class ObtainTokenPairWithView(TokenObtainPairView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = MyTokenObtainPairSerializer


class ManagerCreate(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, format='json'):
        serializer = ManagerSerializer(data=request.data)
        if serializer.is_valid():
            manager = serializer.save()
            if manager:
                json = serializer.data
                return Response(json, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        # Automatically set the user of the profile to the currently authenticated user
        serializer.save(user=self.request.user)


class TeamCreate(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, format='json'):
        serializer = TeamSerializer(data=request.data)
        if serializer.is_valid():
            manager = serializer.save()
            if manager:
                json = serializer.data
                return Response(json, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PlayerCreate(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, format='json'):
        serializer = PlayerDetailSerializer(data=request.data)
        if serializer.is_valid():
            player = serializer.save()
            if player:
                json = serializer.data
                return Response(json, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PlayerAvatarUpdate(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        serializer = PlayerAvatarSerializer(data=request.data)
        if serializer.is_valid():
            player = Player.objects.get(pk=kwargs['playerid'])
            player.avatar_str = serializer.data.get('avatar_str')
            player.avatar = base64_to_image(serializer.data.get('avatar_str'))
            player.save()
            json = serializer.data
            return Response(json, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
def convertToNoneWhenNaN(value):
    if pd.isnull(value):
        return None
    else:
        return value
    
class ImportPlayerAPIView(APIView):
    serializer_class = ImporterSerializer
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        data = request.FILES
        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            excel_file = data.get('file')
            df = pd.read_excel(excel_file, sheet_name=0)
            # df2 = df.where(pd.notnull(df), None)
            players = []
            for index, row in df.iterrows():
                first_name = convertToNoneWhenNaN(row['first_name'])
                last_name = convertToNoneWhenNaN(row['last_name'])
                first_pos = convertToNoneWhenNaN(row['first_pos'])
                second_pos = convertToNoneWhenNaN(row['second_pos'])
                weight = convertToNoneWhenNaN(row['weight'])
                height = convertToNoneWhenNaN(row['height'])
                join_date = convertToNoneWhenNaN(row['join_date'])
                home_town = convertToNoneWhenNaN(row['home_town'])
                jersey_number = convertToNoneWhenNaN(row['jersey_number'])
                phone_number = "0" + convertToNoneWhenNaN(row['phone_number'])
                email = convertToNoneWhenNaN(row['email'])
                bat_hand = convertToNoneWhenNaN(row['bat_hand'])
                throw_hand = convertToNoneWhenNaN(row['throw_hand'])
                short_team_name = convertToNoneWhenNaN(row['short_team_name'])
                team = Team.objects.get(shortName = short_team_name)
                player = Player.objects.filter(phoneNumber=phone_number)
                if player.exists():
                    player[0].delete()
                
                player = Player(
                    firstName = first_name,
                    lastName = last_name,
                    firstPos = first_pos,
                    secondPos = second_pos,
                    team = team,
                    weight = weight,
                    height = height,
                    joinDate = join_date,
                    homeTown = home_town,
                    jerseyNumber =jersey_number,
                    phoneNumber = phone_number,
                    email = email,
                    batHand = bat_hand,
                    throwHand = throw_hand,
                )
                players.append(player)
            Player.objects.bulk_create(players)
            return Response({
                'status': True,
                'message': "Players created successfully"
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class EventCreate(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, format='json'):
        serializer = EventSerializer(data=request.data)
        if serializer.is_valid():
            event = serializer.save()
            if event:
                json = serializer.data
                return Response(json, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class GameCreate(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, format='json'):
        serializer = GameCreateSerializer(data=request.data)
        if serializer.is_valid():
            event = serializer.save()
            if event:
                json = serializer.data
                return Response(json, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ManagerProfile(generics.RetrieveAPIView):
    queryset = Manager.objects.all()
    serializer_class = ManagerSerializer

class TeamProfile(generics.RetrieveAPIView):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer

class PlayerProfile(generics.RetrieveAPIView):
    queryset = Player.objects.all()
    serializer_class = PlayerDetailSerializer

class EventProfile(generics.RetrieveAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer

class PlayerList(generics.ListCreateAPIView):
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return PlayerListSerializer
        return PlayerDetailSerializer
    
    def get_queryset(self):
        team = Team.objects.get(id=self.kwargs['teamid'])
        return Player.objects.filter(team=team)
    
class EventList(generics.ListCreateAPIView):
    serializer_class = EventSerializer
    
    def get_queryset(self):
        team = Team.objects.get(id=self.kwargs['teamid'])
        return Event.objects.filter(team=team)
    
class GameList(generics.ListCreateAPIView):
    serializer_class = GameCreateSerializer
    
    def get_queryset(self):
        team = Team.objects.get(id=self.kwargs['teamid'])
        return Game.objects.filter(team=team)
