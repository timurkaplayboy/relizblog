from django.contrib import admin

from .models import Category, Comment, Post, PostMedia, PostRating, Tag


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


class PostMediaInline(admin.TabularInline):
    model = PostMedia
    extra = 1


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'author',
        'category',
        'status',
        'views_count',
        'published_at',
        'created_at',
    )
    list_filter = ('status', 'category', 'tags', 'created_at', 'published_at')
    search_fields = ('title', 'excerpt', 'content', 'author__username', 'tags__name')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'published_at'
    filter_horizontal = ('tags',)
    inlines = (PostMediaInline,)


@admin.register(PostMedia)
class PostMediaAdmin(admin.ModelAdmin):
    list_display = ('post', 'media_type', 'title', 'created_at')
    list_filter = ('media_type', 'created_at')
    search_fields = ('post__title', 'title')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'author', 'is_active', 'moderated_by', 'moderated_at', 'created_at')
    list_filter = ('is_active', 'created_at', 'moderated_at')
    search_fields = ('post__title', 'author__username', 'text')


@admin.register(PostRating)
class PostRatingAdmin(admin.ModelAdmin):
    list_display = ('post', 'user', 'score', 'created_at')
    list_filter = ('score', 'created_at')
    search_fields = ('post__title', 'user__username', 'user__email')
