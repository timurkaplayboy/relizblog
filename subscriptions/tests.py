from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import NewsletterSubscription


class NewsletterSubscriptionTests(TestCase):
    def test_subscribe_and_unsubscribe_by_token(self):
        User = get_user_model()
        user = User.objects.create_user(
            username='reader',
            email='reader@example.com',
            password='StrongPass12345',
        )
        self.client.login(username='reader', password='StrongPass12345')

        response = self.client.post(
            reverse('subscriptions:newsletter_subscribe'),
            {'email': user.email},
        )

        self.assertEqual(response.status_code, 302)
        subscription = NewsletterSubscription.objects.get(email=user.email)
        self.assertTrue(subscription.is_active)
        self.assertEqual(subscription.user, user)

        response = self.client.post(
            reverse(
                'subscriptions:newsletter_unsubscribe',
                kwargs={'token': subscription.token},
            )
        )

        self.assertEqual(response.status_code, 302)
        subscription.refresh_from_db()
        self.assertFalse(subscription.is_active)
