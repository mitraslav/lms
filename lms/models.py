from django.conf import settings
from django.db import models

class Course(models.Model):
    title =  models.CharField(max_length=255)
    preview = models.ImageField(upload_to='lms/courses/', blank=True, null=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.title

class Lesson(models.Model):
    course = models.ForeignKey(Course, related_name='lessons', on_delete=models.CASCADE)

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    preview = models.ImageField(upload_to="lms/lessons/", blank=True, null=True)
    video_url = models.URLField(max_length=500, blank=True)

    def __str__(self):
        return self.title

class Payment(models.Model):
    CASH = 'cash'
    TRANSFER = 'transfer'

    PAYMENT_METHOD_CHOICES = (
        (CASH, "Наличные"),
        (TRANSFER, "Перевод на счет"),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name="пользователь",
    )
    payment_date = models.DateField(verbose_name="дата оплаты")
    paid_course = models.ForeignKey(
        Course,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payments",
        verbose_name="оплаченный курс",
    )
    paid_lesson = models.ForeignKey(
        Lesson,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payments",
        verbose_name="оплаченный урок",
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="сумма оплаты")
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        verbose_name="способ оплаты",
    )

    def __str__(self):
        target = self.paid_course or self.paid_lesson
        return f"{self.user} - {target} - {self.amount}"

    class Meta:
        verbose_name = "Платеж"
        verbose_name_plural = "Платежи"