from django.contrib import admin

from .models import Category, Comment, Post


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'status', 'published_at', 'created_at')
    list_filter = ('status', 'category', 'created_at', 'published_at')
    search_fields = ('title', 'excerpt', 'content', 'author__username')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'published_at'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'author', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('post__title', 'author__username', 'text')

# Register your models here.
