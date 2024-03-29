from django.urls import include, path
from .views import AcceptJoinRequestView, AtBatList, ErrorPageView, EventCreate, EventList, EventProfile, EventDelete, GameCreate, GameList, ImportPlayerAPIView, JoinTeamRequest, ManagerCreate, ManagerList, ManagerProfile, ObtainTokenPairWithView, PlayerAvatarUpdate, PlayerCreate, PlayerGameList, PlayerList, PlayerProfile, SuccessPageView, TeamCreate, TeamListView, TeamProfile, TransactionCreate, TransactionList, TransactionProfile, UserCreate, UserLogin, TransactionDelete, EquipmentList, EquipmentCreate, EquipmentDelete
from rest_framework_simplejwt import views as jwt_views
from rest_framework.routers import DefaultRouter

# router = DefaultRouter()
# router.register(r'request_jointeam', JoinTeamRequest, basename='requestjointeam')
urlpatterns = [
     path('register/', UserCreate.as_view(), name='register-user'),
     path('login/', UserLogin.as_view(), name='user-login'),
     path('token/obtain/', ObtainTokenPairWithView.as_view(),
         name='token_create'),  # override sjwt stock token
     path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
     path("acceptjointeam/<pk>/",  AcceptJoinRequestView.as_view(), name="accept_jointeam"),
     path("request_jointeam/",  JoinTeamRequest.as_view(), name="request_jointeam"),
     path('success/', SuccessPageView.as_view(), name='success_page'),
     path('error/', ErrorPageView.as_view(), name='error_page'),
     path('manager/profile/<int:pk>/',
         ManagerProfile.as_view(), name="manager_profile"),
     path('team/profile/<int:pk>/',
         TeamProfile.as_view(), name="team_profile"),
     path('teams/', TeamListView.as_view(), name='teams'),
     path('event/profile/<int:pk>/',
         EventProfile.as_view(), name="event_profile"),
     path('event/profile/<int:pk>/',
         EventDelete.as_view(), name="event_delete"),
     path('transaction/profile/<int:pk>/',
         TransactionProfile.as_view(), name="transaction_profile"),
     path('transaction/delete/<int:pk>/',
         TransactionDelete.as_view(), name="transaction_delete"),
     path('transaction/delete/<int:pk>/',
         EquipmentDelete.as_view(), name="equipment_delete"),
     path('player/profile/<int:pk>/',
         PlayerProfile.as_view(), name="player_profile"),
     path('player/update-avatar/<int:playerid>/', PlayerAvatarUpdate.as_view(), name="player_update_avatar"),
     path('manager/create/', ManagerCreate.as_view(), name='manager_create'),
     path('managers/team/<int:teamid>/', ManagerList.as_view(), name='player-list'),
     path('team/create/', TeamCreate.as_view(), name='team_create'),
     path('event/create/', EventCreate.as_view(), name='event_create'),
     path('game/create/', GameCreate.as_view(), name='game_create'),
     path('transaction/create/', TransactionCreate.as_view(), name='transaction_create'),
     path('equipment/create/', EquipmentCreate.as_view(), name='equipment_create'),
     path('player/create/', PlayerCreate.as_view(), name='team_create'),
     path('player/import/', ImportPlayerAPIView.as_view(), name='players_import'),
     path('players/team/<int:teamid>/', PlayerList.as_view(), name='player-list'),
     path('events/team/<int:teamid>/', EventList.as_view(), name='event-list'),
     path('games/team/<int:teamid>/', GameList.as_view(), name='game-list'),
     path('transactions/team/<int:teamid>/', TransactionList.as_view(), name='transaction-list'),
     path('equipments/team/<int:teamid>/', EquipmentList.as_view(), name='equipment-list'),
     path('playergames/game/<int:gameid>/', PlayerGameList.as_view(), name='playergame-list'),
     path('atbats/game/<int:gameid>/', AtBatList.as_view(), name='atbat-list'),
    #  path('', include(router.urls)),
]
