from rest_framework import serializers
from .models import User, Payment
from django.contrib.auth import get_user_model


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "first_name", "last_name", "phone", "city", "avatar")
        read_only_fields = ('id', 'email')

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

class UserSerializer(serializers.ModelSerializer):
    payments = PaymentSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ("id", "email", "payments")

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("id", "email", "password")

        def create(self, validated_data):
            password = validated_data.pop("password")
            user = User(**validated_data)
            user.set_password(password)
            user.save()
            return user