import datetime
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from rest_framework import status, generics
from rest_framework.response import Response
from django.contrib.auth.models import User
from .serializers import AtBatCreateSerializer, AtBatSerializer, CreateManagerSerializer, EventRequestSerializer, EventSerializer, GameCreateSerializer, GameSerializer, ImporterSerializer, LeagueSerializer, ManagerDetailSerializer, ManagerEventSerializer, ManagerListSerializer, NotificationSerializer, PlayerAvatarSerializer, PlayerDetailSerializer, PlayerEventSerializer, PlayerGameCreateSerializer, PlayerGameSerializer, PlayerListSerializer, PlayerListStatSerializer, TeamCreateSerializer, TeamSerializer, TransactionSerializer, UpdateManagerSerializer, UserPushTokenSerializer, UserSerializer, EquipmentSerializer
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import authenticate, login
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import permissions, viewsets
from django.core.mail import send_mail
from rest_framework.permissions import IsAuthenticated
from .models import AtBat, JoinRequest, League, ManagerEvent, Notification, PlayerEvent, PlayerGame, Transaction
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
from django.contrib.auth import update_session_auth_hash
from .serializers import ChangePasswordSerializer


import os
import string
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

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    if request.method == 'POST':
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            if user.check_password(serializer.data.get('old_password')):
                user.set_password(serializer.data.get('new_password'))
                user.save()
                update_session_auth_hash(request, user)  # To update session after password change
                return Response({'message': 'Password changed successfully.'}, status=status.HTTP_200_OK)
            return Response({'message': 'Incorrect old password.'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
            pending_request = JoinRequest.objects.filter(manager=join_request.manager, status=0, team=join_request.team)
            if pending_request.exists():
                return Response({"message": "You have already sent a pending join request to this team."}, status=400)
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
            email_template_path = os.path.join(os.path.dirname(__file__), 'email.html')
            with open(email_template_path, 'r') as f:
                email_template = f.read()
            email_body = email_template.format(
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
    
class EventPlayerRequest(APIView):
    permission_classes = [permissions.IsAuthenticated]
    # queryset = JoinRequest.objects.all()
    # serializer_class = JoinRequestSerializer

    def post(self, request, format='json', **kwargs):
        try:
            event = Event.objects.get(pk=kwargs["eventid"])
        except Event.DoesNotExist:
            return Response({"error": "Event not found"}, status=status.HTTP_404_NOT_FOUND)
        
        managers = Manager.objects.filter(team=event.team)
        players = Player.objects.filter(team=event.team)

        for manager in managers:
            event_manager = ManagerEvent.objects.create(manager=manager, event=event)
            event_manager.save()
            uidb64 = base64.urlsafe_b64encode(force_bytes(event_manager.pk))
            domain = get_current_site(self.request).domain
            accept_link = reverse(
                    "accept_event",
                    kwargs={'pk': event_manager.pk},
                )
            activate_url = "http://" + domain + accept_link
            deny_url = "http://" + domain + reverse("deny_event", kwargs={'pk': event_manager.pk})
            email_subject = "Yêu cầu tham gia sự kiện"
            email_message = "Đây là email từ Baseball management app"
            email_template_path = os.path.join(os.path.dirname(__file__), 'emailEvent.html')
            with open(email_template_path, 'r') as f:
                email_template = f.read()
                timeEnd = "Chưa rõ" if event.timeEnd is None else event.timeEnd
                timeStart = "Chưa rõ" if event.timeStart is None else event.timeStart
                location = "Chưa rõ" if event.location is None else event.location
                email_body = email_template.format(
                firstName=manager.firstName,
                lastName=manager.lastName,
                team=event.team.name,
                title=event.title,
                timeStart=timeStart,
                timeEnd=timeEnd,
                location=location,
                activate_url=activate_url,
                deny_url=deny_url
            )
            send_mail(
                email_subject,
                email_message,
                "thaiduiqn@gmail.com",
                [manager.email],
                fail_silently=False,
                html_message=email_body,
            )
        
        for player in players:
            event_player = PlayerEvent.objects.create(player=player, event=event)
            event_player.save()
            uidb64 = base64.urlsafe_b64encode(force_bytes(event_player.pk))
            domain = get_current_site(self.request).domain
            accept_link = reverse(
                    "accept_event_player",
                    kwargs={'pk': event_player.pk},
                )
            activate_url = "http://" + domain + accept_link
            deny_url = "http://" + domain + reverse("deny_event_player", kwargs={'pk': event_player.pk})
            email_subject = "Yêu cầu tham gia sự kiện"
            email_message = "Đây là email từ Baseball management app"
            email_template_path = os.path.join(os.path.dirname(__file__), 'emailEvent.html')
            with open(email_template_path, 'r') as f:
                email_template = f.read()
                email_body = email_template.format(
                firstName=player.firstName,
                lastName=player.lastName,
                team=event.team.name,
                title=event.title,
                timeStart=event.timeStart,
                timeEnd=event.timeEnd,
                location=event.location,
                activate_url=activate_url,
                deny_url=deny_url
            )
            send_mail(
                email_subject,
                email_message,
                "thaiduiqn@gmail.com",
                [player.email],
                fail_silently=False,
                html_message=email_body,
            )
        return Response({"message": "Emails sent successfully"}, status=status.HTTP_201_CREATED)
    # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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

class AcceptEventView(View):
    def get(self, request, *args, **kwargs):
        manager_event = ManagerEvent.objects.get(pk=kwargs['pk'])

        # Accept the event
        manager_event.status = 1
        manager_event.save()
        return redirect('success_event_page')
    
class AcceptEventPlayerView(View):
    def get(self, request, *args, **kwargs):
        player_event = PlayerEvent.objects.get(pk=kwargs['pk'])

        # Accept the event
        player_event.status = 1
        player_event.save()
        return redirect('success_event_page')

class DenyEventView(View):
    def get(self, request, *args, **kwargs):
        manager_event = ManagerEvent.objects.get(pk=kwargs['pk'])

        # Accept the event
        manager_event.status = 0
        manager_event.save()
        return redirect('deny_event_page')
    
class DenyEventPlayerView(View):
    def get(self, request, *args, **kwargs):
        player_event = PlayerEvent.objects.get(pk=kwargs['pk'])

        # Accept the event
        player_event.status = 0
        player_event.save()
        return redirect('deny_event_page')

class SuccessPageView(TemplateView):
    template_name = "success.html"

class SuccessEventPageView(TemplateView):
    template_name = "success_event.html"

class DenyEventPageView(TemplateView):
    template_name = "deny_event.html"

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
            player : Player = serializer.save()
            if player:
                json = serializer.data
                managers = Manager.objects.filter(team = player.team)

                for manager in managers:
                    Notification.objects.create(
                        manager = manager, 
                        title = "Thêm cầu thủ", 
                        content=f"Cầu thủ #{player.jerseyNumber}.{player.firstName} {player.lastName} vừa được thêm.",
                        time = datetime.datetime.now(),
                        screen = "PlayerProfile",
                        item_id = player.pk
                    )
                return Response(json, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PlayerAvatarUpdate(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        serializer = PlayerAvatarSerializer(data=request.data)
        if serializer.is_valid():
            player = Player.objects.get(pk=kwargs['playerid'])
            player.avatar_str = serializer.data.get('avatar_str')
            if (serializer.validated_data.get('avatar_str')):
                player.avatar = base64_to_image(serializer.data.get('avatar_str'))
            player.save()
            json = serializer.data
            return Response(json, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ManagerUpdate(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        manager = Manager.objects.get(pk=kwargs['pk'])
        serializer = UpdateManagerSerializer(manager, data=request.data, partial=True)
        if serializer.is_valid():
            if (serializer.validated_data.get('avatar_str')):
                manager.avatar = base64_to_image(serializer.validated_data.get('avatar_str'))
            manager.save()
            serializer.save()
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
            managers = Manager.objects.filter(team = players[0].team)

            for manager in managers:
                Notification.objects.create(
                    manager = manager, 
                    title = "Thêm một số cầu thủ", 
                    content=f"Một số cầu thủ vừa được thêm qua file Excel.",
                    time = datetime.datetime.now(),
                    screen = "PlayerList",
                    item_id = None
                )
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
            event : Event = serializer.save()
            if event:
                json = serializer.data
                managers = Manager.objects.filter(team = event.team)

                for manager in managers:
                    Notification.objects.create(
                        manager = manager, 
                        title = "Thêm sự kiện", 
                        content=f"Sự kiện {event.title} bắt đầu lúc {event.timeStart} vừa được thêm.",
                        time = datetime.datetime.now(),
                        screen = "EventDetail",
                        item_id = event.pk
                    )
                return Response(json, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LeagueCreate(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, format='json'):
        serializer = LeagueSerializer(data=request.data)
        if serializer.is_valid():
            league : League = serializer.save()
            if league:
                json = serializer.data
                managers = Manager.objects.filter(team = league.team)

                for manager in managers:
                    Notification.objects.create(
                        manager = manager, 
                        title = "Thêm giải đấu", 
                        content=f"Giải đấu {league.title} vừa được thêm.",
                        time = datetime.datetime.now(),
                        screen = "LeagueDetail",
                        item_id = league.pk
                    )
                return Response(json, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class GameCreate(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, format='json'):
        serializer = GameCreateSerializer(data=request.data)
        if serializer.is_valid():
            game : Game = serializer.save()
            if game:
                json = serializer.data
                managers = Manager.objects.filter(team = game.team)

                for manager in managers:
                    Notification.objects.create(
                        manager = manager, 
                        title = "Cập nhật trận đấu", 
                        content=f"Trận đấu với {game.oppTeam} bắt đầu lúc {game.timeStart} vừa được thêm.",
                        time = datetime.datetime.now(),
                        screen = "GameDetail",
                        item_id = game.pk
                    )
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
            equipment : Equipment = serializer.save()
            if equipment:
                json = serializer.data
                managers = Manager.objects.filter(team = equipment.team)

                for manager in managers:
                    Notification.objects.create(
                        manager = manager, 
                        title = "Thêm dụng cụ", 
                        content=f"Dụng cụ {equipment.name} vừa được thêm.",
                        time = datetime.datetime.now(),
                        screen = "EquipmentDetail",
                        item_id = equipment.pk
                    )
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

class LeagueProfile(generics.RetrieveAPIView):
    queryset = League.objects.all()
    serializer_class = LeagueSerializer

class LeagueDelete(generics.DestroyAPIView):
    queryset = League.objects.all()
    serializer_class = LeagueSerializer

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

class LeagueList(generics.ListCreateAPIView):
    serializer_class = LeagueSerializer
    
    def get_queryset(self):
        team = Team.objects.get(id=self.kwargs['teamid'])
        return League.objects.filter(team=team)
    
class GameList(generics.ListCreateAPIView):
    serializer_class = GameSerializer
    
    def get_queryset(self):
        team = Team.objects.get(id=self.kwargs['teamid'])
        return Game.objects.filter(team=team)
    
class PlayerStatList(generics.ListCreateAPIView):
    serializer_class = PlayerListStatSerializer
    def get_queryset(self):
        team = Team.objects.get(id=self.kwargs['teamid'])
        return Player.objects.filter(team=team)

class PlayerEventList(generics.ListCreateAPIView):
    serializer_class = PlayerEventSerializer
    def get_queryset(self):
        event = Event.objects.get(id=self.kwargs['eventid'])
        return PlayerEvent.objects.filter(event=event)

class ManagerEventList(generics.ListCreateAPIView):
    serializer_class = ManagerEventSerializer
    def get_queryset(self):
        event = Event.objects.get(id=self.kwargs['eventid'])
        return ManagerEvent.objects.filter(event=event)
    
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
    
class NotificationList(generics.ListCreateAPIView):
    serializer_class = NotificationSerializer
    
    def get_queryset(self):
        manager = Manager.objects.get(id=self.kwargs['managerid'])
        return Notification.objects.filter(manager=manager)
    
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
    
class JoinRequestList(generics.ListCreateAPIView):
    serializer_class = JoinRequestSerializer
    
    def get_queryset(self):
        manager = Manager.objects.get(id=self.kwargs['managerid'])
        return JoinRequest.objects.filter(manager=manager)
    
class GameUpdate(generics.UpdateAPIView):
    queryset = Game.objects.all()
    serializer_class = GameCreateSerializer

    def perform_update(self, serializer):
        game : Game = self.get_object()
        serializer.save()
        managers = Manager.objects.filter(team = game.team)

        for manager in managers:
            Notification.objects.create(
                manager = manager, 
                title = "Cập nhật trận đấu", 
                content=f"Thông tin trận đấu với {game.oppTeam} bắt đầu lúc {game.timeStart} vừa được cập nhật.",
                time = datetime.datetime.now(),
                screen = "GameDetail",
                item_id = game.pk
            )

class PlayerUpdate(generics.UpdateAPIView):
    queryset = Player.objects.all()
    serializer_class = PlayerDetailSerializer

    def perform_update(self, serializer):
        player : Player = self.get_object()
        serializer.save()
        managers = Manager.objects.filter(team = player.team)

        for manager in managers:
            Notification.objects.create(
                manager = manager, 
                title = "Cập nhật cầu thủ", 
                content=f"Thông tin cầu thủ #{player.jerseyNumber}.{player.firstName} {player.lastName} vừa được cập nhật.",
                time = datetime.datetime.now(),
                screen = "PlayerProfile",
                item_id = player.pk
            )

class TeamUpdate(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        team = Team.objects.get(pk=kwargs['pk'])
        serializer = TeamSerializer(team, data=request.data, partial=True)
        if serializer.is_valid():
            if (serializer.validated_data.get('logo_str')):
                team.logo = base64_to_image(serializer.validated_data.get('logo_str'))
            team.save()
            serializer.save()
            json = serializer.data
            managers = Manager.objects.filter(team = team)

            for manager in managers:
                Notification.objects.create(
                    manager = manager, 
                    title = "Cập nhật thông tin đội", 
                    content=f"Thông tin của đội bóng vừa được cập nhật.",
                    time = datetime.datetime.now(),
                    screen = "TeamProfile",
                    item_id = team.pk
                )
            return Response(json, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ManagerUpdate(generics.UpdateAPIView):
    queryset = Manager.objects.all()
    serializer_class = UpdateManagerSerializer

class EventUpdate(generics.UpdateAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer

    def perform_update(self, serializer):
        event : Event = self.get_object()
        serializer.save()
        managers = Manager.objects.filter(team = event.team)

        for manager in managers:
            Notification.objects.create(
                manager = manager, 
                title = "Cập nhật sự kiện", 
                content=f"Thông tin sự kiện {event.title} bắt đầu lúc {event.timeStart} vừa được cập nhật.",
                time = datetime.datetime.now(),
                screen = "EventDetail",
                item_id = event.pk
            )

class LeagueUpdate(generics.UpdateAPIView):
    queryset = League.objects.all()
    serializer_class = LeagueSerializer

    def perform_update(self, serializer):
        league : League = self.get_object()
        serializer.save()
        managers = Manager.objects.filter(team = league.team)
        for manager in managers:
            # Create a notification after the game is updated
            Notification.objects.create(
                manager = manager, 
                title = "Cập nhật giải đấu", 
                content=f"Thông tin giải đấu {league.title} vừa được cập nhật.",
                time = datetime.datetime.now(),
                screen = "LeagueDetail",
                item_id = league.pk
            )

class TransactionUpdate(generics.UpdateAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer

class NotificationUpdate(generics.UpdateAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer

class EquipmentUpdate(generics.UpdateAPIView):
    queryset = Equipment.objects.all()
    serializer_class = EquipmentSerializer

    def perform_update(self, serializer):
        equipment : Equipment = self.get_object()
        serializer.save()
        # Create a notification after the game is updated
        managers = Manager.objects.filter(team = equipment.team)
        for manager in managers:
            Notification.objects.create(
                manager = manager, 
                title = "Cập nhật dụng cụ", 
                content=f"Thông tin dụng cụ {equipment.name} vừa được cập nhật.",
                time = datetime.datetime.now(),
                screen = "EquipmentDetail",
                item_id = equipment.pk
            )

class PlayerGameUpdate(generics.UpdateAPIView):
    queryset = PlayerGame.objects.all()
    serializer_class = PlayerGameCreateSerializer

@api_view(['POST'])
def update_player(request):
    players = Player.objects.all()

    fields = ['plateApperance', 'homeRun', 'runBattedIn', 'run', 'single', 'double', 
              'triple', 'baseOnBall', 'intentionalBB', 'hitByPitch', 'strikeOut', 
              'fielderChoice', 'sacrificeFly', 'sacrificeBunt', 'stolenBase', 
              'leftOnBase', 'doublePlay', 'triplePlay', 'onBaseByError', 'putOut', 
              'assist', 'error', 'totalBatterFaced', 'totalInGameOut', 'oppHit', 
              'oppRun', 'earnedRun', 'oppBaseOnBall', 'oppStrikeOut', 'hitBatter', 
              'balk', 'wildPitch', 'oppHomeRun', 'pickOff']
    for player in players:
        try:
            player_game = PlayerGame.objects.get(player=player, game_id=5)
            for field in fields:
                setattr(player, field, getattr(player_game, field))
            player.save()
        except PlayerGame.DoesNotExist:
            continue
    return Response(status=status.HTTP_200_OK)

class TeamStatsView(APIView):
    def get(self, request, team_id, format=None):
        players = Player.objects.filter(team_id=team_id)
        total_pa = sum(player.plateApperance for player in players)
        total_single = sum(player.single for player in players)
        total_double = sum(player.double for player in players)
        total_triple = sum(player.triple for player in players)
        total_hr = sum(player.homeRun for player in players)
        total_rbi = sum(player.runBattedIn for player in players)
        total_run = sum(player.run for player in players)
        total_atBat = sum(player.atBat for player in players)
        total_hit = sum(player.hit for player in players)
        total_bb = sum(player.baseOnBall for player in players)
        total_hbp = sum(player.hitByPitch for player in players)
        total_stolenBase = sum(player.stolenBase for player in players)
        total_strikeOut = sum(player.strikeOut for player in players)
        total_onBaseErr = sum(player.onBaseByError for player in players)
        if (total_atBat == 0): 
            total_avg = '-'
        else:
            total_avg = "{:.3f}".format(total_hit / total_atBat)
        if (total_pa == 0): 
            total_obp = '-'
        else:
            total_obp = "{:.3f}".format((total_hit + total_bb + total_hbp + total_onBaseErr) / total_pa)

        if (total_atBat == 0): 
            total_slg = '-'
        else:
            total_slg = "{:.3f}".format((total_single + total_double*2 + total_triple*3 + total_hr*4) / total_atBat)

        if total_obp == '-' and total_slg == '-':
            total_ops =  '-'
        elif total_obp == '-':
            total_ops =  total_slg
        elif total_slg == '-':
            total_ops =  total_obp
        else:
            total_ops =  "{:.3f}".format(float(total_slg) + float(total_obp))

        total_er = sum(player.earnedRun for player in players)
        total_oppBB = sum(player.oppBaseOnBall for player in players)
        total_oppSO = sum(player.oppStrikeOut for player in players)
        total_oppHit = sum(player.oppHit for player in players)
        total_outs = sum(player.totalInGameOut for player in players)

        up = total_oppBB + total_oppHit
        down = (total_outs // 3) + ((total_outs % 3) / 3)
        if total_outs == 0:
            if up != 0:
                total_whip =  'INF'
            else:
                total_whip =  '-'
        total_whip =  "{:.1f}".format(up/down)

        up = sum(player.earnedRun*27 for player in players)
        down = total_outs
        if down == 0:
            if total_er != 0:
                total_era = 'INF'
            else:
                total_era = '-'
        total_era = "{:.2f}".format(up/down)
    
        return Response({
            'totalPA': total_pa,
            'totalSingle': total_single,
            'totalDouble': total_double,
            'totalTriple': total_triple,
            'totalHR': total_hr,
            'totalRBI': total_rbi,
            'totalRun': total_run,
            'totalAtBat': total_atBat,
            'totalHit': total_hit,
            'totalBB': total_bb,
            'totalHBP': total_hbp,
            'totalStolenBase': total_stolenBase,
            'totalStrikeOut': total_strikeOut,
            'totalOBP': total_obp,
            'totalSLG': total_slg,
            'totalOPS': total_ops,
            'totalAVG': total_avg,
            'totalER': total_er,
            'totalOppBB': total_oppBB,
            'totalOppSO': total_oppSO,
            'totalOppHit': total_oppHit,
            'totalWHIP': total_whip,
            'totalERA': total_era,
        })

class LeaveTeamView(APIView):
    def post(self, request, manager_id):
        manager = get_object_or_404(Manager, id=manager_id)
        join_team = get_object_or_404(JoinRequest, manager=manager, team = manager.team)
        # if manager.user != request.user:
        #     return Response({"error": "You can only leave a team for yourself."}, status=status.HTTP_403_FORBIDDEN)
        
        manager.team = None
        manager.save()
        try:
            join_team.delete()
        except JoinRequest.DoesNotExist:
            pass 
        serializer = ManagerDetailSerializer(manager)
        return Response(serializer.data, status=status.HTTP_200_OK)
