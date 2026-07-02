from django.views.generic import DetailView, ListView

from .models import Announcement


class AnnouncementListView(ListView):
    model = Announcement
    template_name = 'announcements/announcement_list.html'
    context_object_name = 'announcements'
    paginate_by = 10

    def get_queryset(self):
        return Announcement.objects.filter(is_active=True)


class AnnouncementDetailView(DetailView):
    model = Announcement
    template_name = 'announcements/announcement_detail.html'
    context_object_name = 'announcement'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return Announcement.objects.filter(is_active=True)

# Create your views here.
