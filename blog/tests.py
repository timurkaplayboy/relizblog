from django.contrib.auth import get_user_model
from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from accounts.models import Profile

from subscriptions.models import NewsletterSubscription

from .models import Category, Comment, Post, PostMedia, PostRating, Tag


class BlogViewsTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.author = User.objects.create_user(
            username='author',
            email='author@example.com',
            password='StrongPass12345',
        )
        self.author.profile.role = Profile.Role.AUTHOR
        self.author.profile.save()

        self.reader = User.objects.create_user(
            username='reader',
            email='reader@example.com',
            password='StrongPass12345',
        )
        self.category = Category.objects.create(name='Релізи', slug='releases')
        self.tag = Tag.objects.create(name='Django', slug='django')
        self.post = Post.objects.create(
            title='Перша стаття',
            slug='first-post',
            author=self.author,
            category=self.category,
            excerpt='Коротко',
            content='Повний текст статті',
            status=Post.Status.PUBLISHED,
        )
        self.post.tags.add(self.tag)

    def test_public_can_view_published_posts_and_filters(self):
        urls = [
            reverse('blog:post_list'),
            reverse('blog:post_detail', kwargs={'slug': self.post.slug}),
            reverse('blog:category_detail', kwargs={'category_slug': self.category.slug}),
            reverse('blog:tag_detail', kwargs={'tag_slug': self.tag.slug}),
        ]

        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, self.post.title)

    def test_reader_cannot_create_post(self):
        self.client.login(username='reader', password='StrongPass12345')

        response = self.client.get(reverse('blog:post_create'))

        self.assertEqual(response.status_code, 403)

    def test_author_can_create_post(self):
        self.client.login(username='author', password='StrongPass12345')

        response = self.client.post(
            reverse('blog:post_create'),
            {
                'title': 'Нова стаття',
                'slug': 'new-post',
                'category': self.category.pk,
                'tags': [self.tag.pk],
                'excerpt': 'Опис',
                'content': 'Текст нової статті',
                'status': Post.Status.PUBLISHED,
                'media_items-TOTAL_FORMS': '2',
                'media_items-INITIAL_FORMS': '0',
                'media_items-MIN_NUM_FORMS': '0',
                'media_items-MAX_NUM_FORMS': '1000',
                'media_items-0-media_type': 'image',
                'media_items-0-file': SimpleUploadedFile(
                    'cover.jpg',
                    b'image-bytes',
                    content_type='image/jpeg',
                ),
                'media_items-0-title': '',
                'media_items-1-media_type': 'video',
                'media_items-1-file': SimpleUploadedFile(
                    'release.mp4',
                    b'video-bytes',
                    content_type='video/mp4',
                ),
                'media_items-1-title': 'Відео релізу',
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Post.objects.filter(slug='new-post', author=self.author).exists())
        self.assertEqual(PostMedia.objects.filter(post__slug='new-post').count(), 2)

    def test_comment_create_delete_and_moderate_permissions(self):
        self.client.login(username='reader', password='StrongPass12345')
        response = self.client.post(
            reverse('blog:comment_create', kwargs={'slug': self.post.slug}),
            {'text': 'Гарна стаття'},
        )

        self.assertEqual(response.status_code, 302)
        comment = Comment.objects.get(author=self.reader)

        response = self.client.get(reverse('blog:comment_delete', kwargs={'pk': comment.pk}))
        self.assertEqual(response.status_code, 200)

        self.client.logout()
        self.client.login(username='author', password='StrongPass12345')
        response = self.client.post(
            reverse('blog:comment_moderate', kwargs={'pk': comment.pk}),
            {'is_active': ''},
        )

        self.assertEqual(response.status_code, 302)
        comment.refresh_from_db()
        self.assertFalse(comment.is_active)
        self.assertEqual(comment.moderated_by, self.author)

    def test_reader_can_rate_post_and_average_is_calculated(self):
        self.client.login(username='reader', password='StrongPass12345')

        response = self.client.post(
            reverse('blog:post_rate', kwargs={'slug': self.post.slug}),
            {'score': 4},
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(PostRating.objects.get(post=self.post, user=self.reader).score, 4)
        self.assertEqual(self.post.average_rating, 4)

    @override_settings(
        EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
        SITE_URL='https://example.test',
    )
    def test_new_published_post_sends_email_to_subscribers(self):
        NewsletterSubscription.objects.create(email='subscriber@example.com')

        Post.objects.create(
            title='Email post',
            slug='email-post',
            author=self.author,
            content='Text',
            status=Post.Status.PUBLISHED,
        )

        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Email post', mail.outbox[0].subject)
        self.assertIn('/subscriptions/newsletter/unsubscribe/', mail.outbox[0].body)
