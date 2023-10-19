from django.urls import path
from .views import ObtainTokenPairWithView, UserCreate, UserLogin
from rest_framework_simplejwt import views as jwt_views

urlpatterns = [
    path('register/', UserCreate.as_view(), name='register-user'),
    path('login/', UserLogin.as_view(), name='user-login'),
    path('token/obtain/', ObtainTokenPairWithView.as_view(),
         name='token_create'),  # override sjwt stock token
    path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
]
