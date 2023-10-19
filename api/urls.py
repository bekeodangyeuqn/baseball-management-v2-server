from django.urls import path
from .views import register_user, UserLogin

urlpatterns = [
    path('register/', register_user, name='register-user'),
    path('login/', UserLogin.as_view(), name='user-login'),
]
