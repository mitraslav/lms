from rest_framework import generics
from rest_framework.permissions import AllowAny
from .filters import PaymentFilter
from .models import User, Payment
from .serializers import UserProfileSerializer, PaymentSerializer, RegisterSerializer


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
