from django.shortcuts import get_object_or_404
from rest_framework import viewsets, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from .models import Course, Lesson, Subscription
from .permissions import IsModer, IsOwner
from .serializers import CourseSerializer, LessonSerializer
from .paginators import BasePagination

from django.utils import timezone
from datetime import timedelta
from lms.tasks import send_course_update_email


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.prefetch_related('lessons')
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = BasePagination

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.groups.filter(name="moderators").exists():
            return qs
        return qs.filter(owner=self.request.user)

    def get_permissions(self):
        if self.action == "create":
            # модератор не может создавать
            return [IsAuthenticated(), ~IsModer()]
        if self.action == "destroy":
            # модератор не может удалять; немодератор может удалять только свое
            return [IsAuthenticated(), IsOwner(), ~IsModer()]
        if self.action in ("update", "partial_update"):
            # редактировать может модератор или владелец
            return [IsAuthenticated(), (IsModer() | IsOwner())]
        # list/retrieve: доступ авторизованным, а queryset ограничит немодераторов
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def perform_update(self, serializer):
        course = serializer.save()

        now = timezone.now()
        if course.last_notified_at and now - course.last_notified_at <= timedelta(hours=4):
            return

        subscribers = course.subscribers.all()  # или ваша связь подписок
        for user in subscribers:
            if user.email:
                send_course_update_email.delay(user.email, course.title)

        course.last_notified_at = now
        course.save(update_fields=["last_notified_at"])


# ---- LESSONS (Generics) ----

class LessonBaseQuerysetMixin:
    """
    Ограничиваем доступ к объектам:
    - модератор видит все
    - остальные видят только свои
    """
    def get_queryset(self):
        qs = Lesson.objects.all()
        if self.request.user.groups.filter(name="moderators").exists():
            return qs
        return qs.filter(owner=self.request.user)


class LessonListAPIView(LessonBaseQuerysetMixin, generics.ListAPIView):
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = BasePagination


class LessonRetrieveAPIView(LessonBaseQuerysetMixin, generics.RetrieveAPIView):
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated]


class LessonCreateAPIView(LessonBaseQuerysetMixin, generics.CreateAPIView):
    serializer_class = LessonSerializer
    # модератор не может создавать
    permission_classes = [IsAuthenticated, ~IsModer]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class LessonUpdateAPIView(LessonBaseQuerysetMixin, generics.UpdateAPIView):
    serializer_class = LessonSerializer
    # редактировать может модератор ИЛИ владелец
    permission_classes = [IsAuthenticated, IsModer | IsOwner]


class LessonDestroyAPIView(LessonBaseQuerysetMixin, generics.DestroyAPIView):
    serializer_class = LessonSerializer
    # модератор не может удалять; владелец (немодератор) может удалять свое
    permission_classes = [IsAuthenticated, IsOwner, ~IsModer]

class SubscriptionToggleAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        course_id = kwargs.get("pk") or request.data.get("course_id")
        course = get_object_or_404(Course, pk=course_id)

        subs_qs = Subscription.objects.filter(user=user, course=course)
        if subs_qs.exists():
            subs_qs.delete()
            return Response({"message": "подписка удалена", "subscribed": False})

        Subscription.objects.create(user=user, course=course)
        return Response({"message": "подписка добавлена", "subscribed": True})