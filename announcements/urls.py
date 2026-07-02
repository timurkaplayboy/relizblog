from django.urls import path

from .views import AnnouncementDetailView, AnnouncementListView

app_name = 'announcements'

urlpatterns = [
    path('', AnnouncementListView.as_view(), name='list'),
    path('<slug:slug>/', AnnouncementDetailView.as_view(), name='detail'),
]
