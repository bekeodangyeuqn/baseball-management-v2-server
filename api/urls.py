from django.urls import path
from .views import EventCreate, EventProfile, ImportPlayerAPIView, ManagerCreate, ManagerProfile, ObtainTokenPairWithView, PlayerCreate, PlayerProfile, TeamCreate, TeamProfile, UserCreate, UserLogin
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
     path('manager/create/', ManagerCreate.as_view(), name='manager_create'),
     path('team/create/', TeamCreate.as_view(), name='team_create'),
     path('event/create/', EventCreate.as_view(), name='event_create'),
     path('player/create/', PlayerCreate.as_view(), name='team_create'),
     path('player/import/', ImportPlayerAPIView.as_view(), name='players_import'),
]
