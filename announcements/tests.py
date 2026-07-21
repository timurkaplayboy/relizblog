from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from accounts.models import Profile

from .models import Announcement


class AnnouncementCrudTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.author = User.objects.create_user(
            username='author',
            email='author@example.com',
            password='StrongPass12345',
        )
        self.author.profile.role = Profile.Role.AUTHOR
        self.author.profile.save()

    def test_author_can_create_update_and_delete_announcement(self):
        self.client.login(username='author', password='StrongPass12345')

        response = self.client.post(
            reverse('announcements:create'),
            {
                'title': 'Новий реліз',
                'slug': 'new-release',
                'body': 'Публікуємо важливе оновлення.',
                'priority': Announcement.Priority.HIGH,
                'is_active': 'on',
            },
        )

        self.assertEqual(response.status_code, 302)
        announcement = Announcement.objects.get(slug='new-release')

        response = self.client.post(
            reverse('announcements:update', kwargs={'slug': announcement.slug}),
            {
                'title': 'Оновлений реліз',
                'slug': 'new-release',
                'body': 'Оновлений текст.',
                'priority': Announcement.Priority.MEDIUM,
                'is_active': 'on',
            },
        )

        self.assertEqual(response.status_code, 302)
        announcement.refresh_from_db()
        self.assertEqual(announcement.title, 'Оновлений реліз')

        response = self.client.post(
            reverse('announcements:delete', kwargs={'slug': announcement.slug})
        )

        self.assertEqual(response.status_code, 302)
        self.assertFalse(Announcement.objects.filter(pk=announcement.pk).exists())
