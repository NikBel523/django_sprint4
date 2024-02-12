from django.contrib import admin

from .models import Category, Comment, Location, Post

admin.site.empty_value_display = 'Не здано'


class PostAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'title',
        # 'text',
        'pub_date',
        'author',
        'location',
        'category',
        'is_published',
    )

    list_editable = (
        'is_published',
        'pub_date',
        'category'
    )

    list_per_page = 10


class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'description',
        'is_published',
    )

    list_editable = (
        'description',
        'is_published',
    )

    list_per_page = 10


class CategoryComment(admin.ModelAdmin):
    list_display = (
        'text',
        'post',
        'author',
        'created_at',
    )


admin.site.register(Location)
admin.site.register(Comment, CategoryComment)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Post, PostAdmin)
