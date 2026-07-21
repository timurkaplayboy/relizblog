from django import forms

from .models import NewsletterSubscription


class NewsletterSubscriptionForm(forms.ModelForm):
    class Meta:
        model = NewsletterSubscription
        fields = ('email',)
        labels = {
            'email': 'Email для повідомлень',
        }
        widgets = {
            'email': forms.EmailInput(attrs={'placeholder': 'you@example.com'}),
        }

    def clean_email(self):
        return self.cleaned_data['email'].lower()
