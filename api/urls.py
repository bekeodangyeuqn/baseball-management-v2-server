from django.urls import path
from .views import EventCreate, EventList, EventProfile, GameCreate, GameList, ImportPlayerAPIView, ManagerCreate, ManagerProfile, ObtainTokenPairWithView, PlayerAvatarUpdate, PlayerCreate, PlayerList, PlayerProfile, TeamCreate, TeamProfile, UserCreate, UserLogin
from rest_framework_simplejwt import views as jwt_views

urlpatterns = [
     path('register/', UserCreate.as_view(), name='register-user'),
     path('login/', UserLogin.as_view(), name='user-login'),
     path('token/obtain/', ObtainTokenPairWithView.as_view(),
         name='token_create'),  # override sjwt stock token
     path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
     path('manager/profile/<int:pk>/',
         ManagerProfile.as_view(), name="manager_profile"),
     path('team/profile/<int:pk>/',
         TeamProfile.as_view(), name="team_profile"),
     path('event/profile/<int:pk>/',
         EventProfile.as_view(), name="event_profile"),
     path('player/profile/<int:pk>/',
         PlayerProfile.as_view(), name="player_profile"),
     path('player/update-avatar/<int:playerid>/', PlayerAvatarUpdate.as_view(), name="player_update_avatar"),
     path('manager/create/', ManagerCreate.as_view(), name='manager_create'),
     path('team/create/', TeamCreate.as_view(), name='team_create'),
     path('event/create/', EventCreate.as_view(), name='event_create'),
     path('game/create/', GameCreate.as_view(), name='game_create'),
     path('player/create/', PlayerCreate.as_view(), name='team_create'),
     path('player/import/', ImportPlayerAPIView.as_view(), name='players_import'),
     path('players/team/<int:teamid>/', PlayerList.as_view(), name='player-list'),
     path('events/team/<int:teamid>', EventList.as_view(), name='event-list'),
     path('games/team/<int:teamid>', GameList.as_view(), name='game-list'),
]
