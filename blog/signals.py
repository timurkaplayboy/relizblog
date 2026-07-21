from django.conf import settings
from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver

from subscriptions.models import NewsletterSubscription

from .models import Post


@receiver(post_save, sender=Post)
def notify_subscribers_about_new_post(sender, instance, created, **kwargs):
    was_published_before = getattr(instance, '_was_published_before', False)
    should_notify = instance.status == Post.Status.PUBLISHED and (created or not was_published_before)

    if not should_notify:
        return

    site_url = settings.SITE_URL.rstrip('/')
    post_url = f'{site_url}{instance.get_absolute_url()}'
    subject = f'Нова стаття на RelizBlog: {instance.title}'

    for subscription in NewsletterSubscription.objects.filter(is_active=True):
        unsubscribe_url = f'{site_url}{subscription.get_unsubscribe_url()}'
        message = (
            f'Привіт! На RelizBlog опубліковано нову статтю:\\n\\n'
            f'{instance.title}\\n{post_url}\\n\\n'
            f'Щоб відписатися від повідомлень, перейдіть за посиланням:\\n'
            f'{unsubscribe_url}'
        )
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [subscription.email],
            fail_silently=True,
        )
