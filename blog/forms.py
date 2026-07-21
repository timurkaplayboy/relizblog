from django import forms
from django.forms import inlineformset_factory

from .models import Category, Comment, Post, PostMedia, PostRating, Tag


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = (
            'title',
            'slug',
            'category',
            'tags',
            'excerpt',
            'content',
            'cover_image',
            'status',
        )
        labels = {
            'title': 'Заголовок',
            'slug': 'Slug',
            'category': 'Категорія',
            'tags': 'Теги',
            'excerpt': 'Короткий опис',
            'content': 'Текст',
            'cover_image': 'Обкладинка',
            'status': 'Статус',
        }
        help_texts = {
            'slug': 'Можна залишити порожнім, Django створить slug автоматично.',
            'tags': 'Утримуйте Command/Ctrl, щоб обрати кілька тегів.',
        }
        widgets = {
            'content': forms.Textarea(attrs={'rows': 12}),
            'excerpt': forms.Textarea(attrs={'rows': 3}),
        }


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ('name', 'slug', 'description')
        labels = {
            'name': 'Назва',
            'slug': 'Slug',
            'description': 'Опис',
        }
        help_texts = {
            'slug': 'Можна залишити порожнім.',
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }


class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ('name', 'slug')
        labels = {
            'name': 'Назва',
            'slug': 'Slug',
        }
        help_texts = {
            'slug': 'Можна залишити порожнім.',
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        labels = {
            'text': 'Коментар',
        }
        widgets = {
            'text': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Напишіть коментар...'}),
        }

    def clean_text(self):
        text = self.cleaned_data['text'].strip()
        if len(text) < 3:
            raise forms.ValidationError('Коментар має містити щонайменше 3 символи.')
        if len(text) > 2000:
            raise forms.ValidationError('Коментар не може бути довшим за 2000 символів.')
        return text


class CommentModerationForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('is_active',)
        labels = {
            'is_active': 'Активний',
        }


class PostRatingForm(forms.ModelForm):
    class Meta:
        model = PostRating
        fields = ('score',)
        labels = {
            'score': 'Оцінка',
        }
        widgets = {
            'score': forms.RadioSelect(
                choices=[(score, f'{score}') for score in range(1, 6)]
            ),
        }

    def clean_score(self):
        score = self.cleaned_data['score']
        if score < 1 or score > 5:
            raise forms.ValidationError('Оцінка має бути від 1 до 5.')
        return score


class PostMediaForm(forms.ModelForm):
    class Meta:
        model = PostMedia
        fields = ('media_type', 'file', 'title')
        labels = {
            'media_type': 'Тип',
            'file': 'Файл',
            'title': 'Підпис',
        }

    def clean(self):
        cleaned_data = super().clean()
        media_type = cleaned_data.get('media_type')
        file = cleaned_data.get('file')

        if not file:
            return cleaned_data

        extension = file.name.rsplit('.', 1)[-1].lower()
        image_extensions = {'jpg', 'jpeg', 'png', 'webp', 'gif'}
        video_extensions = {'mp4', 'webm', 'mov'}

        if media_type == PostMedia.MediaType.IMAGE and extension not in image_extensions:
            raise forms.ValidationError('Для фото можна завантажити jpg, jpeg, png, webp або gif.')
        if media_type == PostMedia.MediaType.VIDEO and extension not in video_extensions:
            raise forms.ValidationError('Для відео можна завантажити mp4, webm або mov.')

        return cleaned_data


PostMediaFormSet = inlineformset_factory(
    Post,
    PostMedia,
    form=PostMediaForm,
    fields=('media_type', 'file', 'title'),
    extra=2,
    can_delete=True,
)
