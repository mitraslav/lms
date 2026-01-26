from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from .filters import PaymentFilter
from .models import User, Payment
from .permissions import IsSelfOrStaff
from .serializers import UserProfileSerializer, PaymentSerializer, RegisterSerializer, UserSerializer


class UserProfileUpdateAPIView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer

class PaymentListAPIView(generics.ListAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    filterset_class = PaymentFilter
    ordering_fields = ["payment_date"]
    ordering = ["-payment_date"]

class RegisterAPIView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ("update", "partial_update", "destroy"):
            return [IsAuthenticated(), IsSelfOrStaff()]
        return [IsAuthenticated()]
