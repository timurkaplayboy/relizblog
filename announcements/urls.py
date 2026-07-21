from django.urls import path

from .views import (
    AnnouncementCreateView,
    AnnouncementDeleteView,
    AnnouncementDetailView,
    AnnouncementListView,
    AnnouncementUpdateView,
)

app_name = 'announcements'

urlpatterns = [
    path('', AnnouncementListView.as_view(), name='list'),
    path('create/', AnnouncementCreateView.as_view(), name='create'),
    path('<slug:slug>/edit/', AnnouncementUpdateView.as_view(), name='update'),
    path('<slug:slug>/delete/', AnnouncementDeleteView.as_view(), name='delete'),
    path('<slug:slug>/', AnnouncementDetailView.as_view(), name='detail'),
]
