from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from blog.views import AuthorRequiredMixin

from .forms import AnnouncementForm
from .models import Announcement


class AnnouncementListView(ListView):
    model = Announcement
    template_name = 'announcements/announcement_list.html'
    context_object_name = 'announcements'
    paginate_by = 10

    def get_queryset(self):
        if self.request.user.is_authenticated and (
            self.request.user.is_staff
            or self.request.user.is_superuser
            or getattr(getattr(self.request.user, 'profile', None), 'role', None) in ('author', 'admin')
        ):
            return Announcement.objects.all()
        return Announcement.objects.filter(is_active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['can_manage_announcements'] = self.request.user.is_authenticated and (
            self.request.user.is_staff
            or self.request.user.is_superuser
            or getattr(getattr(self.request.user, 'profile', None), 'role', None) in ('author', 'admin')
        )
        return context


class AnnouncementDetailView(DetailView):
    model = Announcement
    template_name = 'announcements/announcement_detail.html'
    context_object_name = 'announcement'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        if self.request.user.is_authenticated and (
            self.request.user.is_staff
            or self.request.user.is_superuser
            or getattr(getattr(self.request.user, 'profile', None), 'role', None) in ('author', 'admin')
        ):
            return Announcement.objects.all()
        return Announcement.objects.filter(is_active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['can_manage_announcements'] = self.request.user.is_authenticated and (
            self.request.user.is_staff
            or self.request.user.is_superuser
            or getattr(getattr(self.request.user, 'profile', None), 'role', None) in ('author', 'admin')
        )
        return context


class AnnouncementCreateView(AuthorRequiredMixin, CreateView):
    model = Announcement
    form_class = AnnouncementForm
    template_name = 'announcements/announcement_form.html'

    def form_valid(self, form):
        messages.success(self.request, 'Оголошення створено.')
        return super().form_valid(form)


class AnnouncementUpdateView(AuthorRequiredMixin, UpdateView):
    model = Announcement
    form_class = AnnouncementForm
    template_name = 'announcements/announcement_form.html'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def form_valid(self, form):
        messages.success(self.request, 'Оголошення оновлено.')
        return super().form_valid(form)


class AnnouncementDeleteView(AuthorRequiredMixin, DeleteView):
    model = Announcement
    template_name = 'announcements/announcement_confirm_delete.html'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    success_url = reverse_lazy('announcements:list')

    def form_valid(self, form):
        messages.success(self.request, 'Оголошення видалено.')
        return super().form_valid(form)
