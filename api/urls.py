from django.urls import path
from .views import AcceptJoinRequestView, EventCreate, EventList, EventProfile, GameCreate, GameList, ImportPlayerAPIView, JoinTeamRequest, ManagerCreate, ManagerList, ManagerProfile, ObtainTokenPairWithView, PlayerAvatarUpdate, PlayerCreate, PlayerList, PlayerProfile, SuccessPageView, TeamCreate, TeamListView, TeamProfile, UserCreate, UserLogin
from rest_framework_simplejwt import views as jwt_views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'request_jointeam', JoinTeamRequest)
urlpatterns = [
     path('register/', UserCreate.as_view(), name='register-user'),
     path('login/', UserLogin.as_view(), name='user-login'),
     path('token/obtain/', ObtainTokenPairWithView.as_view(),
         name='token_create'),  # override sjwt stock token
     path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
     path("acceptjointeam/<pk>/",  AcceptJoinRequestView.as_view(), name="accept_jointeam"),
     path('success/', SuccessPageView.as_view(), name='success_page'),
     path('manager/profile/<int:pk>/',
         ManagerProfile.as_view(), name="manager_profile"),
     path('team/profile/<int:pk>/',
         TeamProfile.as_view(), name="team_profile"),
         path('teams/', TeamListView.as_view(), name='teams'),
     path('event/profile/<int:pk>/',
         EventProfile.as_view(), name="event_profile"),
     path('player/profile/<int:pk>/',
         PlayerProfile.as_view(), name="player_profile"),
     path('player/update-avatar/<int:playerid>/', PlayerAvatarUpdate.as_view(), name="player_update_avatar"),
     path('manager/create/', ManagerCreate.as_view(), name='manager_create'),
     path('managers/team/<int:teamid>/', ManagerList.as_view(), name='player-list'),
     path('team/create/', TeamCreate.as_view(), name='team_create'),
     path('event/create/', EventCreate.as_view(), name='event_create'),
     path('game/create/', GameCreate.as_view(), name='game_create'),
     path('player/create/', PlayerCreate.as_view(), name='team_create'),
     path('player/import/', ImportPlayerAPIView.as_view(), name='players_import'),
     path('players/team/<int:teamid>/', PlayerList.as_view(), name='player-list'),
     path('events/team/<int:teamid>/', EventList.as_view(), name='event-list'),
     path('games/team/<int:teamid>/', GameList.as_view(), name='game-list'),
]
