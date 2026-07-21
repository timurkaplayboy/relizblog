from django import forms

from .models import Announcement


class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ('title', 'slug', 'body', 'priority', 'is_active', 'starts_at', 'ends_at')
        labels = {
            'title': 'Заголовок',
            'slug': 'Slug',
            'body': 'Текст',
            'priority': 'Пріоритет',
            'is_active': 'Активне',
            'starts_at': 'Початок',
            'ends_at': 'Завершення',
        }
        help_texts = {
            'slug': 'Можна залишити порожнім.',
        }
        widgets = {
            'body': forms.Textarea(attrs={'rows': 8}),
            'starts_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'ends_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
