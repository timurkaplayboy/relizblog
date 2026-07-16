from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .forms import (
    CategoryForm,
    CommentForm,
    CommentModerationForm,
    PostForm,
    PostMediaFormSet,
    TagForm,
)
from .models import Category, Comment, Post, Tag


def user_role(user):
    if not user.is_authenticated:
        return None
    profile = getattr(user, 'profile', None)
    return getattr(profile, 'role', None)


def is_blog_admin(user):
    return (
        user.is_authenticated
        and (
            user.is_superuser
            or user.is_staff
            or user_role(user) == 'admin'
        )
    )


def is_author_or_admin(user):
    return is_blog_admin(user) or user_role(user) == 'author'


def can_manage_post(user, post):
    return is_blog_admin(user) or (user.is_authenticated and post.author_id == user.id)


def visible_posts_for_user(user):
    queryset = Post.objects.select_related('author', 'category').prefetch_related('tags')
    if is_blog_admin(user):
        return queryset
    if user.is_authenticated:
        return queryset.filter(status=Post.Status.PUBLISHED) | queryset.filter(author=user)
    return queryset.filter(status=Post.Status.PUBLISHED)


class AuthorRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return is_author_or_admin(self.request.user)

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        raise PermissionDenied('У вас немає прав для цієї дії.')


class PostOwnerRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return can_manage_post(self.request.user, self.get_object())

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        raise PermissionDenied('Ви можете редагувати лише власні статті.')


class PostMediaFormSetMixin:
    def get_media_formset(self):
        if self.request.method == 'POST':
            return PostMediaFormSet(
                self.request.POST,
                self.request.FILES,
                instance=getattr(self, 'object', None),
            )
        return PostMediaFormSet(instance=getattr(self, 'object', None))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.setdefault('media_formset', self.get_media_formset())
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        if not self.object.pk:
            self.object.author = self.request.user

        media_formset = PostMediaFormSet(
            self.request.POST,
            self.request.FILES,
            instance=self.object,
        )
        if not media_formset.is_valid():
            return self.form_invalid(form)

        self.object.save()
        form.save_m2m()
        media_formset.instance = self.object
        media_formset.save()
        messages.success(self.request, self.success_message)
        return redirect(self.object.get_absolute_url())

    def form_invalid(self, form):
        media_formset = PostMediaFormSet(
            self.request.POST,
            self.request.FILES,
            instance=getattr(self, 'object', None),
        )
        return self.render_to_response(
            self.get_context_data(form=form, media_formset=media_formset)
        )


class PostListView(ListView):
    model = Post
    template_name = 'blog/post_list.html'
    context_object_name = 'posts'
    paginate_by = 6

    def get_queryset(self):
        queryset = visible_posts_for_user(self.request.user).distinct()
        self.category = None
        self.tag = None

        category_slug = self.kwargs.get('category_slug') or self.request.GET.get('category')
        tag_slug = self.kwargs.get('tag_slug') or self.request.GET.get('tag')
        status = self.request.GET.get('status')

        if category_slug:
            self.category = get_object_or_404(Category, slug=category_slug)
            queryset = queryset.filter(category=self.category)

        if tag_slug:
            self.tag = get_object_or_404(Tag, slug=tag_slug)
            queryset = queryset.filter(tags=self.tag)

        if status in dict(Post.Status.choices):
            if status == Post.Status.DRAFT and not is_author_or_admin(self.request.user):
                queryset = queryset.none()
            else:
                queryset = queryset.filter(status=status)
        elif not is_author_or_admin(self.request.user):
            queryset = queryset.filter(status=Post.Status.PUBLISHED)

        return queryset.order_by('-published_at', '-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                'categories': Category.objects.all(),
                'tags': Tag.objects.all(),
                'current_category': self.category,
                'current_tag': self.tag,
                'current_status': self.request.GET.get('status', ''),
                'can_create_post': is_author_or_admin(self.request.user),
                'pagination_query': self.get_pagination_query('page'),
            }
        )
        return context

    def get_pagination_query(self, page_param):
        query = self.request.GET.copy()
        query.pop(page_param, None)
        return query.urlencode()


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/post_detail.html'
    context_object_name = 'post'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return (
            visible_posts_for_user(self.request.user)
            .select_related('author', 'category')
            .prefetch_related('tags', 'media_items')
            .distinct()
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        comments = self.object.comments.select_related('author')
        can_moderate = can_manage_post(self.request.user, self.object)
        if not can_moderate:
            comments = comments.filter(is_active=True)

        paginator = Paginator(comments, 5)
        page_obj = paginator.get_page(self.request.GET.get('comments_page'))
        query = self.request.GET.copy()
        query.pop('comments_page', None)

        context.update(
            {
                'comment_form': CommentForm(),
                'comment_page_obj': page_obj,
                'comments': page_obj.object_list,
                'can_manage_post': can_moderate,
                'can_comment': self.request.user.is_authenticated
                and self.object.status == Post.Status.PUBLISHED,
                'comment_pagination_query': query.urlencode(),
            }
        )
        return context


class PostCreateView(AuthorRequiredMixin, PostMediaFormSetMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/post_form.html'
    success_message = 'Статтю створено.'


class PostUpdateView(PostOwnerRequiredMixin, PostMediaFormSetMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/post_form.html'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    success_message = 'Статтю оновлено.'


class PostDeleteView(PostOwnerRequiredMixin, DeleteView):
    model = Post
    template_name = 'blog/post_confirm_delete.html'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    success_url = reverse_lazy('blog:post_list')

    def form_valid(self, form):
        messages.success(self.request, 'Статтю видалено.')
        return super().form_valid(form)


class CategoryListView(AuthorRequiredMixin, ListView):
    model = Category
    template_name = 'blog/category_list.html'
    context_object_name = 'categories'


class CategoryCreateView(AuthorRequiredMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'blog/category_form.html'
    success_url = reverse_lazy('blog:category_list')

    def form_valid(self, form):
        messages.success(self.request, 'Категорію створено.')
        return super().form_valid(form)


class CategoryUpdateView(AuthorRequiredMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'blog/category_form.html'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    success_url = reverse_lazy('blog:category_list')

    def form_valid(self, form):
        messages.success(self.request, 'Категорію оновлено.')
        return super().form_valid(form)


class CategoryDeleteView(AuthorRequiredMixin, DeleteView):
    model = Category
    template_name = 'blog/category_confirm_delete.html'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    success_url = reverse_lazy('blog:category_list')

    def form_valid(self, form):
        messages.success(self.request, 'Категорію видалено.')
        return super().form_valid(form)


class TagListView(AuthorRequiredMixin, ListView):
    model = Tag
    template_name = 'blog/tag_list.html'
    context_object_name = 'tags'


class TagCreateView(AuthorRequiredMixin, CreateView):
    model = Tag
    form_class = TagForm
    template_name = 'blog/tag_form.html'
    success_url = reverse_lazy('blog:tag_list')

    def form_valid(self, form):
        messages.success(self.request, 'Тег створено.')
        return super().form_valid(form)


class TagUpdateView(AuthorRequiredMixin, UpdateView):
    model = Tag
    form_class = TagForm
    template_name = 'blog/tag_form.html'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    success_url = reverse_lazy('blog:tag_list')

    def form_valid(self, form):
        messages.success(self.request, 'Тег оновлено.')
        return super().form_valid(form)


class TagDeleteView(AuthorRequiredMixin, DeleteView):
    model = Tag
    template_name = 'blog/tag_confirm_delete.html'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    success_url = reverse_lazy('blog:tag_list')

    def form_valid(self, form):
        messages.success(self.request, 'Тег видалено.')
        return super().form_valid(form)


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm

    def dispatch(self, request, *args, **kwargs):
        self.article = get_object_or_404(
            Post,
            slug=self.kwargs['slug'],
            status=Post.Status.PUBLISHED,
        )
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.post = self.article
        form.instance.author = self.request.user
        messages.success(self.request, 'Коментар додано.')
        return super().form_valid(form)

    def form_invalid(self, form):
        for errors in form.errors.values():
            for error in errors:
                messages.error(self.request, error)
        return redirect(self.get_success_url())

    def get_success_url(self):
        return f'{self.article.get_absolute_url()}#comments'


class CommentDeleteView(LoginRequiredMixin, DeleteView):
    model = Comment
    template_name = 'blog/comment_confirm_delete.html'

    def get_queryset(self):
        queryset = Comment.objects.select_related('post', 'author')
        if is_blog_admin(self.request.user):
            return queryset
        return queryset.filter(author=self.request.user) | queryset.filter(post__author=self.request.user)

    def get_success_url(self):
        return f'{self.object.post.get_absolute_url()}#comments'

    def form_valid(self, form):
        messages.success(self.request, 'Коментар видалено.')
        return super().form_valid(form)


class CommentModerateView(LoginRequiredMixin, UpdateView):
    model = Comment
    form_class = CommentModerationForm
    template_name = 'blog/comment_moderate.html'

    def get_queryset(self):
        queryset = Comment.objects.select_related('post', 'author')
        if is_blog_admin(self.request.user):
            return queryset
        return queryset.filter(post__author=self.request.user)

    def form_valid(self, form):
        form.instance.moderated_by = self.request.user
        form.instance.moderated_at = timezone.now()
        messages.success(self.request, 'Коментар промодеровано.')
        return super().form_valid(form)

    def get_success_url(self):
        return f'{self.object.post.get_absolute_url()}#comments'
