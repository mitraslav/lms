from rest_framework import serializers

from .models import Course, Lesson, Payment

class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = '__all__'

class CourseSerializer(serializers.ModelSerializer):
    lessons_count = serializers.SerializerMethodField()
    lessons = LessonSerializer(source='lesson_set', many=True, read_only=True)

    class Meta:
        model = Course
        fields = '__all__'

    def get_lessons_count(self, obj):
        return obj.lesson_set.count()

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = "__all__"

    def validate(self, attrs):
        course = attrs.get("paid_course")
        lesson = attrs.get("paid_lesson")

        if bool(course) == bool(lesson):
            raise serializers.ValidationError(
                "Нужно указать либо paid_course, либо paid_lesson (строго одно)."
            )
        return attrs