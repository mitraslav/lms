from django.urls import path

from users.apps import UsersConfig
from .views import UserProfileUpdateAPIView, RegisterAPIView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)

app_name = UsersConfig.name

urlpatterns = [
    path("users/<int:pk>/", UserProfileUpdateAPIView.as_view(), name='user-profile-update'),
    path("api/auth/token/refresh/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/auth/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("api/auth/register/", RegisterAPIView.as_view(), name="register")
]