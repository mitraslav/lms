from django.contrib.auth import get_user_model
from django.core.management import BaseCommand

from lms.models import Course, Lesson, Payment
from datetime import date


class Command(BaseCommand):
    help = "Load demo payments"

    def handle(self, *args, **options):
        User = get_user_model()
        user = User.objects.first()
        course = Course.objects.first()
        lesson = Lesson.objects.first()

        Payment.objects.get_or_create(
            user=user,
            payment_date=date(2026, 1, 10),
            paid_course=course,
            paid_lesson=None,
            amount="1990.00",
            payment_method=Payment.TRANSFER,
        )

        Payment.objects.get_or_create(
            user=user,
            payment_date=date(2026, 1, 12),
            paid_course=None,
            paid_lesson=lesson,
            amount="490.00",
            payment_method=Payment.CASH,
        )

        self.stdout.write(self.style.SUCCESS("Payments loaded"))