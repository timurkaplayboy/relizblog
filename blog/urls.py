from django.urls import path

from .views import (
    CategoryCreateView,
    CategoryDeleteView,
    CategoryListView,
    CategoryUpdateView,
    CommentCreateView,
    CommentDeleteView,
    CommentModerateView,
    PostCreateView,
    PostDeleteView,
    PostDetailView,
    PostListView,
    PostUpdateView,
    TagCreateView,
    TagDeleteView,
    TagListView,
    TagUpdateView,
)

app_name = 'blog'

urlpatterns = [
    path('', PostListView.as_view(), name='post_list'),
    path('create/', PostCreateView.as_view(), name='post_create'),
    path('categories/', CategoryListView.as_view(), name='category_list'),
    path('categories/create/', CategoryCreateView.as_view(), name='category_create'),
    path('categories/<slug:slug>/edit/', CategoryUpdateView.as_view(), name='category_update'),
    path('categories/<slug:slug>/delete/', CategoryDeleteView.as_view(), name='category_delete'),
    path('category/<slug:category_slug>/', PostListView.as_view(), name='category_detail'),
    path('tags/', TagListView.as_view(), name='tag_list'),
    path('tags/create/', TagCreateView.as_view(), name='tag_create'),
    path('tags/<slug:slug>/edit/', TagUpdateView.as_view(), name='tag_update'),
    path('tags/<slug:slug>/delete/', TagDeleteView.as_view(), name='tag_delete'),
    path('tag/<slug:tag_slug>/', PostListView.as_view(), name='tag_detail'),
    path('<slug:slug>/', PostDetailView.as_view(), name='post_detail'),
    path('<slug:slug>/edit/', PostUpdateView.as_view(), name='post_update'),
    path('<slug:slug>/delete/', PostDeleteView.as_view(), name='post_delete'),
    path('<slug:slug>/comments/create/', CommentCreateView.as_view(), name='comment_create'),
    path('comments/<int:pk>/moderate/', CommentModerateView.as_view(), name='comment_moderate'),
    path('comments/<int:pk>/delete/', CommentDeleteView.as_view(), name='comment_delete'),
]
