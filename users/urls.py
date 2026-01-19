from django.urls import path

from users.apps import UsersConfig
from .views import UserProfileUpdateAPIView

app_name = UsersConfig.name

urlpatterns = [
    path("users/<int:pk>/", UserProfileUpdateAPIView.as_view(), name='user-profile-update')
]