import django_filters
from users.models import Payment

class PaymentFilter(django_filters.FilterSet):
    paid_course = django_filters.NumberFilter(field_name="paid_course_id")
    paid_lesson = django_filters.NumberFilter(field_name="paid_lesson_id")
    payment_method = django_filters.CharFilter(field_name="payment_method")

    class Meta:
        model = Payment
        fields = ["paid_course", "paid_lesson", "payment_method"]