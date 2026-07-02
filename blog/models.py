from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.text import slugify

from core.models import TimeStampedModel


class Category(TimeStampedModel):
    name = models.CharField(max_length=120, unique=True, verbose_name='Назва')
    slug = models.SlugField(max_length=140, unique=True, blank=True, verbose_name='Slug')
    description = models.TextField(blank=True, verbose_name='Опис')

    class Meta:
        ordering = ('name',)
        verbose_name = 'Категорія'
        verbose_name_plural = 'Категорії'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Post(TimeStampedModel):
    class Status(models.TextChoices):
        DRAFT = 'draft', 'Чернетка'
        PUBLISHED = 'published', 'Опубліковано'

    title = models.CharField(max_length=200, verbose_name='Заголовок')
    slug = models.SlugField(max_length=220, unique=True, blank=True, verbose_name='Slug')
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор',
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name='posts',
        blank=True,
        null=True,
        verbose_name='Категорія',
    )
    excerpt = models.CharField(max_length=255, blank=True, verbose_name='Короткий опис')
    content = models.TextField(verbose_name='Текст')
    cover_image = models.FileField(
        upload_to='blog/covers/',
        blank=True,
        null=True,
        verbose_name='Обкладинка',
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        verbose_name='Статус',
    )
    published_at = models.DateTimeField(blank=True, null=True, verbose_name='Дата публікації')

    class Meta:
        ordering = ('-published_at', '-created_at')
        verbose_name = 'Публікація'
        verbose_name_plural = 'Публікації'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('blog:post_detail', kwargs={'slug': self.slug})

    def __str__(self):
        return self.title


class Comment(TimeStampedModel):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Публікація',
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор',
    )
    text = models.TextField(verbose_name='Коментар')
    is_active = models.BooleanField(default=True, verbose_name='Активний')

    class Meta:
        ordering = ('-created_at',)
        verbose_name = 'Коментар'
        verbose_name_plural = 'Коментарі'

    def __str__(self):
        return f'{self.author} -> {self.post}'

# Create your models here.
