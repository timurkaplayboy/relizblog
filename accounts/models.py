from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.db import models

from core.models import TimeStampedModel


class Profile(TimeStampedModel):
    class Role(models.TextChoices):
        USER = 'user', 'User'
        AUTHOR = 'author', 'Author'
        ADMIN = 'admin', 'Admin'

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name='Користувач',
    )
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.USER,
        verbose_name='Роль',
    )
    bio = models.TextField(blank=True, verbose_name='Про себе')
    avatar = models.FileField(
        upload_to='avatars/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'webp', 'gif'])],
        verbose_name='Аватар',
    )

    class Meta:
        verbose_name = 'Профіль'
        verbose_name_plural = 'Профілі'

    def __str__(self):
        return f'{self.user.username} ({self.get_role_display()})'
