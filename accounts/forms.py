from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from .models import Profile

User = get_user_model()


class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
        labels = {
            'username': 'Логін',
            'email': 'Email',
            'first_name': "Ім'я",
            'last_name': 'Прізвище',
        }
        help_texts = {
            'username': '',
        }

    email = forms.EmailField(required=True, label='Email')
    first_name = forms.CharField(required=False, label="Ім'я")
    last_name = forms.CharField(required=False, label='Прізвище')

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Користувач із таким email вже існує.')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data.get('first_name', '').strip()
        user.last_name = self.cleaned_data.get('last_name', '').strip()
        if commit:
            user.save()
        return user


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')
        labels = {
            'first_name': "Ім'я",
            'last_name': 'Прізвище',
            'email': 'Email',
        }

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        queryset = User.objects.filter(email__iexact=email)
        if self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise forms.ValidationError('Користувач із таким email вже існує.')
        return email


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('bio', 'avatar')
        labels = {
            'bio': 'Про себе',
            'avatar': 'Аватар',
        }
