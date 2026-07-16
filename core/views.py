from django.views.generic import TemplateView

from announcements.models import Announcement
from blog.models import Post


class HomeView(TemplateView):
    template_name = 'core/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                'latest_posts': Post.objects.filter(status=Post.Status.PUBLISHED)[:3],
                'latest_announcements': Announcement.objects.filter(is_active=True)[:3],
            }
        )
        return context
