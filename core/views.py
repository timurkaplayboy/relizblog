from django.shortcuts import render

from announcements.models import Announcement
from blog.models import Post


def home(request):
    latest_posts = Post.objects.filter(status=Post.Status.PUBLISHED)[:3]
    latest_announcements = Announcement.objects.filter(is_active=True)[:3]
    return render(
        request,
        'core/home.html',
        {
            'latest_posts': latest_posts,
            'latest_announcements': latest_announcements,
        },
    )

# Create your views here.
