from django.db import models
from django.urls import reverse
from django.utils.text import slugify

from core.models import TimeStampedModel


class Announcement(TimeStampedModel):
    class Priority(models.TextChoices):
        LOW = 'low', 'Низький'
        MEDIUM = 'medium', 'Середній'
        HIGH = 'high', 'Високий'

    title = models.CharField(max_length=200, verbose_name='Заголовок')
    slug = models.SlugField(max_length=220, unique=True, blank=True, verbose_name='Slug')
    body = models.TextField(verbose_name='Текст')
    priority = models.CharField(
        max_length=20,
        choices=Priority.choices,
        default=Priority.MEDIUM,
        verbose_name='Пріоритет',
    )
    is_active = models.BooleanField(default=True, verbose_name='Активне')
    starts_at = models.DateTimeField(blank=True, null=True, verbose_name='Початок')
    ends_at = models.DateTimeField(blank=True, null=True, verbose_name='Завершення')

    class Meta:
        ordering = ('-created_at',)
        verbose_name = 'Оголошення'
        verbose_name_plural = 'Оголошення'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True) or 'announcement'
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('announcements:detail', kwargs={'slug': self.slug})

    def __str__(self):
        return self.title
