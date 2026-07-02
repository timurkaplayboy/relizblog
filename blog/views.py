from django.views.generic import DetailView, ListView

from .models import Post


class PostListView(ListView):
    model = Post
    template_name = 'blog/post_list.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        return (
            Post.objects.select_related('author', 'category')
            .filter(status=Post.Status.PUBLISHED)
        )


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/post_detail.html'
    context_object_name = 'post'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return (
            Post.objects.select_related('author', 'category')
            .prefetch_related('comments')
            .filter(status=Post.Status.PUBLISHED)
        )

# Create your views here.
