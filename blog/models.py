from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify

from core.models import TimeStampedModel


def make_unique_slug(instance, source_value, slug_field='slug'):
    base_slug = slugify(source_value, allow_unicode=True) or 'item'
    slug = base_slug
    model = instance.__class__
    counter = 2

    queryset = model.objects.filter(**{slug_field: slug})
    if instance.pk:
        queryset = queryset.exclude(pk=instance.pk)

    while queryset.exists():
        slug = f'{base_slug}-{counter}'
        queryset = model.objects.filter(**{slug_field: slug})
        if instance.pk:
            queryset = queryset.exclude(pk=instance.pk)
        counter += 1

    return slug


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
            self.slug = make_unique_slug(self, self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('blog:category_detail', kwargs={'category_slug': self.slug})

    def __str__(self):
        return self.name


class Tag(TimeStampedModel):
    name = models.CharField(max_length=80, unique=True, verbose_name='Назва')
    slug = models.SlugField(max_length=100, unique=True, blank=True, verbose_name='Slug')

    class Meta:
        ordering = ('name',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = make_unique_slug(self, self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('blog:tag_detail', kwargs={'tag_slug': self.slug})

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
    tags = models.ManyToManyField(Tag, related_name='posts', blank=True, verbose_name='Теги')
    excerpt = models.CharField(max_length=255, blank=True, verbose_name='Короткий опис')
    content = models.TextField(verbose_name='Текст')
    cover_image = models.FileField(
        upload_to='blog/covers/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'webp', 'gif'])],
        verbose_name='Обкладинка',
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        verbose_name='Статус',
    )
    published_at = models.DateTimeField(blank=True, null=True, verbose_name='Дата публікації')
    views_count = models.PositiveIntegerField(default=0, verbose_name='Перегляди')

    class Meta:
        ordering = ('-published_at', '-created_at')
        verbose_name = 'Публікація'
        verbose_name_plural = 'Публікації'

    def save(self, *args, **kwargs):
        self._was_published_before = False
        if self.pk:
            old_status = Post.objects.filter(pk=self.pk).values_list('status', flat=True).first()
            self._was_published_before = old_status == self.Status.PUBLISHED

        if not self.slug:
            self.slug = make_unique_slug(self, self.title)
        if self.status == self.Status.PUBLISHED and not self.published_at:
            self.published_at = timezone.now()
        if self.status == self.Status.DRAFT:
            self.published_at = None
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('blog:post_detail', kwargs={'slug': self.slug})

    def __str__(self):
        return self.title

    @property
    def average_rating(self):
        value = self.ratings.aggregate(models.Avg('score'))['score__avg']
        return round(value or 0, 1)

    @property
    def ratings_count(self):
        return self.ratings.count()


class PostMedia(TimeStampedModel):
    class MediaType(models.TextChoices):
        IMAGE = 'image', 'Фото'
        VIDEO = 'video', 'Відео'

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='media_items',
        verbose_name='Стаття',
    )
    media_type = models.CharField(
        max_length=20,
        choices=MediaType.choices,
        default=MediaType.IMAGE,
        verbose_name='Тип',
    )
    file = models.FileField(
        upload_to='blog/media/',
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'webp', 'gif', 'mp4', 'webm', 'mov'])],
        verbose_name='Файл',
    )
    title = models.CharField(max_length=160, blank=True, verbose_name='Підпис')

    class Meta:
        ordering = ('created_at',)
        verbose_name = 'Медіа статті'
        verbose_name_plural = 'Медіа статей'

    def __str__(self):
        return self.title or f'{self.get_media_type_display()} для {self.post}'


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
    moderated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='moderated_comments',
        blank=True,
        null=True,
        verbose_name='Модератор',
    )
    moderated_at = models.DateTimeField(blank=True, null=True, verbose_name='Дата модерації')

    class Meta:
        ordering = ('-created_at',)
        verbose_name = 'Коментар'
        verbose_name_plural = 'Коментарі'

    def __str__(self):
        return f'{self.author} -> {self.post}'


class PostRating(TimeStampedModel):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='ratings',
        verbose_name='Стаття',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='post_ratings',
        verbose_name='Користувач',
    )
    score = models.PositiveSmallIntegerField(verbose_name='Оцінка')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=('post', 'user'), name='unique_post_rating_per_user'),
            models.CheckConstraint(
                condition=models.Q(score__gte=1) & models.Q(score__lte=5),
                name='post_rating_score_between_1_and_5',
            ),
        ]
        ordering = ('-created_at',)
        verbose_name = 'Оцінка статті'
        verbose_name_plural = 'Оцінки статей'

    def __str__(self):
        return f'{self.post} - {self.score}/5'
