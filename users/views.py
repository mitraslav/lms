from django.conf import settings
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from lms.models import Course
from .filters import PaymentFilter
from .models import User, Payment
from .permissions import IsSelfOrStaff
from .serializers import UserProfileSerializer, PaymentSerializer, RegisterSerializer, UserSerializer
from .services import create_product, create_price, create_checkout_session


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

class CoursePaymentCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        course_id = request.data.get("course_id")
        course = get_object_or_404(Course, pk=course_id)

        if not hasattr(course, "price"):
            return Response({"detail": "Course has no price field"}, status=400)

        payment = Payment.objects.create(
            user=request.user,
            payment_date=timezone.now().date(),
            paid_course=course,
            amount=course.price,
            payment_method=Payment.TRANSFER,  # или CASH, как хочешь
        )

        product = create_product(name=course.title, description=getattr(course, "description", "") or None)
        price = create_price(product_id=product["id"], amount=float(payment.amount), currency=settings.STRIPE_CURRENCY)
        session = create_checkout_session(price_id=price["id"])

        payment.stripe_product_id = product["id"]
        payment.stripe_price_id = price["id"]
        payment.stripe_session_id = session["id"]
        payment.stripe_payment_url = session.get("url")
        payment.stripe_status = "open"
        payment.save()

        return Response(
            {
                "payment": PaymentSerializer(payment).data,
                "payment_url": payment.stripe_payment_url,
            },
            status=201,
        )
