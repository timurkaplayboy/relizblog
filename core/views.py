from django.views.generic import TemplateView

from announcements.models import Announcement
from blog.models import Category, Post, Tag
from blog.views import popular_posts


class HomeView(TemplateView):
    template_name = 'core/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                'latest_posts': Post.objects.filter(status=Post.Status.PUBLISHED)[:3],
                'latest_announcements': Announcement.objects.filter(is_active=True)[:3],
                'popular_posts': popular_posts(4),
                'categories': Category.objects.all()[:8],
                'tags': Tag.objects.all()[:12],
                'published_posts_count': Post.objects.filter(status=Post.Status.PUBLISHED).count(),
                'categories_count': Category.objects.count(),
                'tags_count': Tag.objects.count(),
            }
        )
        return context
