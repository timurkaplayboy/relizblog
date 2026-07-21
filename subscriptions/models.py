from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.crypto import get_random_string

from core.models import TimeStampedModel


class SubscriptionPlan(TimeStampedModel):
    name = models.CharField(max_length=120, unique=True, verbose_name='Назва')
    description = models.TextField(blank=True, verbose_name='Опис')
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name='Ціна')
    duration_days = models.PositiveIntegerField(default=30, verbose_name='Тривалість у днях')
    is_active = models.BooleanField(default=True, verbose_name='Активний')

    class Meta:
        ordering = ('price', 'name')
        verbose_name = 'Тариф'
        verbose_name_plural = 'Тарифи'

    def __str__(self):
        return self.name


class Subscription(TimeStampedModel):
    class Status(models.TextChoices):
        ACTIVE = 'active', 'Активна'
        CANCELED = 'canceled', 'Скасована'
        EXPIRED = 'expired', 'Завершена'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name='Користувач',
    )
    plan = models.ForeignKey(
        SubscriptionPlan,
        on_delete=models.PROTECT,
        related_name='subscriptions',
        verbose_name='Тариф',
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
        verbose_name='Статус',
    )
    start_date = models.DateField(verbose_name='Дата початку')
    end_date = models.DateField(verbose_name='Дата завершення')

    class Meta:
        ordering = ('-start_date',)
        verbose_name = 'Підписка'
        verbose_name_plural = 'Підписки'

    def __str__(self):
        return f'{self.user} - {self.plan}'


class NewsletterSubscription(TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='newsletter_subscriptions',
        blank=True,
        null=True,
        verbose_name='Користувач',
    )
    email = models.EmailField(unique=True, verbose_name='Email')
    is_active = models.BooleanField(default=True, verbose_name='Активна')
    token = models.CharField(max_length=64, unique=True, blank=True, verbose_name='Token')

    class Meta:
        ordering = ('-created_at',)
        verbose_name = 'Email-підписка'
        verbose_name_plural = 'Email-підписки'

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = get_random_string(48)
        self.email = self.email.lower()
        super().save(*args, **kwargs)

    def get_unsubscribe_url(self):
        return reverse('subscriptions:newsletter_unsubscribe', kwargs={'token': self.token})

    def __str__(self):
        return self.email
