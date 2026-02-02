from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model

@shared_task
def deactivate_inactive_users():
    User = get_user_model()
    cutoff = timezone.now() - timedelta(days=30)

    qs = User.objects.filter(is_active=True).exclude(last_login__isnull=True).filter(last_login__lt=cutoff)
    qs.update(is_active=False)
    return qs.count()
