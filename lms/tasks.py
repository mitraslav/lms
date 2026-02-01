from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def send_course_update_email(user_email: str, course_title: str):
    send_mail(
        subject=f"Обновление курса: {course_title}",
        message=f"Материалы курса «{course_title}» были обновлены.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user_email],
        fail_silently=False,
    )
