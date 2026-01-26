from rest_framework import viewsets, generics
from rest_framework.permissions import IsAuthenticated

from .models import Course, Lesson
from .permissions import IsModer, IsOwner
from .serializers import CourseSerializer, LessonSerializer


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.prefetch_related('lesson_set')
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]

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
