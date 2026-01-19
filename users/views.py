from rest_framework import generics
from .models import User
from .serializers import UserProfileSerializer

class UserProfileUpdateAPIView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer