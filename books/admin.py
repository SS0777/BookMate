from django.contrib import admin
from .models import Category, Book

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'rating', 'category', 'published', 'created']
    list_filter = ['created', 'category', 'rating']
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ['title', 'author', 'description']