import datetime
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from rest_framework import status, generics
from rest_framework.response import Response
from django.contrib.auth.models import User
from .serializers import AtBatCreateSerializer, AtBatSerializer, CreateManagerSerializer, EventSerializer, GameCreateSerializer, GameSerializer, ImporterSerializer, ManagerDetailSerializer, ManagerListSerializer, PlayerAvatarSerializer, PlayerDetailSerializer, PlayerGameCreateSerializer, PlayerGameSerializer, PlayerListSerializer, TeamCreateSerializer, TeamSerializer, TransactionSerializer, UserPushTokenSerializer, UserSerializer, EquipmentSerializer
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import api_view
from rest_framework import status
from django.contrib.auth import authenticate, login
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import permissions, viewsets
from django.core.mail import send_mail
from .models import AtBat, JoinRequest, PlayerGame, Transaction
from .serializers import JoinRequestSerializer
from .serializers import MyTokenObtainPairSerializer
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from .models import Event, Game, Manager, Player, Team, Equipment, UserPushToken
import pandas as pd
import numpy as np
import base64
from django.core.files.base import ContentFile
import string
import random
from .utils import token_generator
from django.views import View
from django.views.generic import TemplateView
from rest_framework.pagination import PageNumberPagination

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

class SeedPushToken(APIView):
    permission_classes = (permissions.AllowAny,)
    authentication_classes = ()
    def post(self, request, *args, **kwargs):
        users = Manager.objects.all()
        for user in users:
            userPushToken = UserPushToken.objects.create(manager=user, push_token=None)
            userPushToken.save()
        return Response({"message": "Push tokens seeded successfully."}, status=status.HTTP_200_OK)

class UpdatePushToken(generics.UpdateAPIView):
    queryset = UserPushToken.objects.all()
    serializer_class = UserPushTokenSerializer

    def get_object(self):
        manager_id = self.kwargs.get('manager_id')
        return get_object_or_404(UserPushToken, manager__id=manager_id)

class PushTokenList(generics.ListAPIView):
    serializer_class = UserPushTokenSerializer

    def get_queryset(self):
        team_id = self.kwargs.get('team_id')
        team = get_object_or_404(Team, id=team_id)
        return UserPushToken.objects.filter(manager__team=team)
    
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
        serializer = CreateManagerSerializer(data=request.data)
        if serializer.is_valid():
            manager = serializer.save()
            if manager:
                json = serializer.data
                userPushToken = UserPushToken.objects.create(manager=manager, push_token=None)
                userPushToken.save()
                return Response(json, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        # Automatically set the user of the profile to the currently authenticated user
        serializer.save(user=self.request.user)

class JoinTeamRequest(APIView):
    permission_classes = [permissions.IsAuthenticated]
    # queryset = JoinRequest.objects.all()
    # serializer_class = JoinRequestSerializer

    def post(self, request, format='json'):
        serializer = JoinRequestSerializer(data=request.data)
        if serializer.is_valid():
            join_request = serializer.save()
            join_request.created_at = datetime.datetime.now()
            join_request.save()
            managers = Manager.objects.filter(team=join_request.team)
            uidb64 = base64.urlsafe_b64encode(force_bytes(join_request.pk))

            domain = get_current_site(self.request).domain
            link = reverse(
                    "accept_jointeam",
                    kwargs={'pk': join_request.pk},
                )
            activate_url = "http://" + domain + link
            email_subject = "Yêu cầu trở thành nhà quản lý"
            email_message = "Đây là email từ Baseball management app"
            with open('../templates/email.html', 'r') as f:
                email_template = string.Template(f.read())
            email_body = email_template.substitute(
            firstName=join_request.manager.firstName,
            lastName=join_request.manager.lastName,
            activate_url=activate_url
        )
            for manager in managers:
                send_mail(
                    email_subject,
                    email_message,
                    "thaiduiqn@gmail.com",
                    [manager.email],
                    fail_silently=False,
                    html_message=email_body,
                )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AcceptJoinRequestView(View):
    def get(self, request, *args, **kwargs):
        join_request = JoinRequest.objects.get(pk=kwargs['pk'])

        # Accept the join request
        join_request.accepted = 1
        manager = join_request.manager
        if manager.team != None:
            return redirect('error_page')
        manager.team = join_request.team
        manager.save()
        join_request.save()

        # Add the user to the team

        return redirect('success_page')

class SuccessPageView(TemplateView):
    template_name = "success.html"

class ErrorPageView(TemplateView):
    template_name = "error.html"

class TeamCreate(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, format='json'):
        serializer = TeamCreateSerializer(data=request.data)
        if serializer.is_valid():
            team = serializer.save()
            if team:
                json = serializer.data
                return Response(json, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TeamListPagination(PageNumberPagination):
    page_size = 10
    page_query_param = 'page'
    max_page_size = 1000

class TeamListView(generics.ListAPIView):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    pagination_class = TeamListPagination

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
                birth_date = convertToNoneWhenNaN(row['birth_date'])
                home_town = convertToNoneWhenNaN(row['home_town'])
                jersey_number = convertToNoneWhenNaN(row['jersey_number'])
                phone_number = "0" + str(convertToNoneWhenNaN(row['phone_number']))
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
                    birthDate = birth_date,
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
            game = serializer.save()
            if game:
                json = serializer.data
                return Response(json, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class TransactionCreate(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, format='json'):
        serializer = TransactionSerializer(data=request.data)
        if serializer.is_valid():
            transaction = serializer.save()
            if transaction:
                json = serializer.data
                return Response(json, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class EquipmentCreate(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, format='json'):
        serializer = EquipmentSerializer(data=request.data)
        if serializer.is_valid():
            equipment = serializer.save()
            if equipment:
                json = serializer.data
                return Response(json, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class PlayerGameCreate(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, format='json'):
        serializer = PlayerGameCreateSerializer(data=request.data)
        if serializer.is_valid():
            playergame = serializer.save()
            if playergame:
                json = serializer.data
                return Response(json, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class AtBatCreate(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, format='json'):
        serializer = AtBatCreateSerializer(data=request.data)
        if serializer.is_valid():
            atbat = serializer.save()
            if atbat:
                json = serializer.data
                return Response(json, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class ManagerProfile(generics.RetrieveAPIView):
    queryset = Manager.objects.all()
    serializer_class = ManagerDetailSerializer

class TeamProfile(generics.RetrieveAPIView):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer

class PlayerProfile(generics.RetrieveAPIView):
    queryset = Player.objects.all()
    serializer_class = PlayerDetailSerializer

class GameProfile(generics.RetrieveAPIView):
    queryset = Game.objects.all()
    serializer_class = GameCreateSerializer

class EventProfile(generics.RetrieveAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer

class EventDelete(generics.DestroyAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer

class TransactionProfile(generics.RetrieveAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer

class TransactionDelete(generics.DestroyAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer

class EquipmentProfile(generics.RetrieveAPIView):
    queryset = Equipment.objects.all()
    serializer_class = EquipmentSerializer

class EquipmentDelete(generics.DestroyAPIView):
    queryset = Equipment.objects.all()
    serializer_class = EquipmentSerializer

class PlayerList(generics.ListCreateAPIView):
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return PlayerListSerializer
        return PlayerDetailSerializer
    
    def get_queryset(self):
        team = Team.objects.get(id=self.kwargs['teamid'])
        return Player.objects.filter(team=team)
    
class ManagerList(generics.ListCreateAPIView):
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ManagerListSerializer
        return ManagerDetailSerializer
    
    def get_queryset(self):
        team = Team.objects.get(id=self.kwargs['teamid'])
        return Manager.objects.filter(team=team)
    
class EventList(generics.ListCreateAPIView):
    serializer_class = EventSerializer
    
    def get_queryset(self):
        team = Team.objects.get(id=self.kwargs['teamid'])
        return Event.objects.filter(team=team)
    
class GameList(generics.ListCreateAPIView):
    serializer_class = GameSerializer
    
    def get_queryset(self):
        team = Team.objects.get(id=self.kwargs['teamid'])
        return Game.objects.filter(team=team)
    
class TransactionList(generics.ListCreateAPIView):
    serializer_class = TransactionSerializer
    
    def get_queryset(self):
        team = Team.objects.get(id=self.kwargs['teamid'])
        return Transaction.objects.filter(team=team)
    
class EquipmentList(generics.ListCreateAPIView):
    serializer_class = EquipmentSerializer
    
    def get_queryset(self):
        team = Team.objects.get(id=self.kwargs['teamid'])
        return Equipment.objects.filter(team=team)
    
class AtBatList(generics.ListCreateAPIView):
    serializer_class = AtBatSerializer
    
    def get_queryset(self):
        game = Game.objects.get(id=self.kwargs['gameid'])
        return AtBat.objects.filter(game=game)
    
class PlayerGameList(generics.ListCreateAPIView):
    serializer_class = PlayerGameSerializer
    
    def get_queryset(self):
        game = Game.objects.get(id=self.kwargs['gameid'])
        return PlayerGame.objects.filter(game=game)
    
class GameUpdate(generics.UpdateAPIView):
    queryset = Game.objects.all()
    serializer_class = GameCreateSerializer

class PlayerUpdate(generics.UpdateAPIView):
    queryset = Player.objects.all()
    serializer_class = PlayerDetailSerializer

class EventUpdate(generics.UpdateAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer

class TransactionUpdate(generics.UpdateAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer

class EquipmentUpdate(generics.UpdateAPIView):
    queryset = Equipment.objects.all()
    serializer_class = EquipmentSerializer

class PlayerGameUpdate(generics.UpdateAPIView):
    queryset = PlayerGame.objects.all()
    serializer_class = PlayerGameCreateSerializer
