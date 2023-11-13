from django.shortcuts import render
from rest_framework import status, generics
from rest_framework.response import Response
from django.contrib.auth.models import User
from .serializers import EventSerializer, ImporterSerializer, ManagerSerializer, PlayerSerializer, TeamSerializer, UserSerializer
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from django.contrib.auth import authenticate, login
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import permissions
from .serializers import MyTokenObtainPairSerializer
from .models import Event, Manager, Player, Team
import pandas as pd
import numpy as np


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
        serializer = PlayerSerializer(data=request.data)
        if serializer.is_valid():
            player = serializer.save()
            if player:
                json = serializer.data
                return Response(json, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
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
            df.replace(np.nan, "")
            players = []
            for index, row in df.iterrows():
                first_name = row['first_name']
                last_name = row['last_name']
                first_pos = row['first_pos']
                second_pos = row['second_pos']
                weight = row['weight']
                height = row['height']
                join_date = row['join_date']
                home_town = row['home_town']
                jersey_number = row['jersey_number']
                phone_number = row['phone_number']
                email = row['email']
                bat_hand = row['bat_hand']
                throw_hand = row['throw_hand']
                short_team_name = row['short_team_name']
                team = Team.objects.get(shortName = short_team_name)
                # player = Player.objects.get(phoneNumber=phone_number)
                # if player is not None:
                #     player.delete()
                
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


class ManagerProfile(generics.RetrieveAPIView):
    queryset = Manager.objects.all()
    serializer_class = ManagerSerializer

class TeamProfile(generics.RetrieveAPIView):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer

class PlayerProfile(generics.RetrieveAPIView):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer

class EventProfile(generics.RetrieveAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
