from django.contrib import admin

from .models import Post, Group, Comment, Follow


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """Представляет модель Post в интерфейсе администратора."""

    list_display = ('pk', 'text', 'pub_date', 'author', 'group')
    list_editable = ('group',)
    search_fields = ('text',)
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Представляет модель Comment в интерфейсе администратора."""

    list_display = ('pk', 'text', 'pub_date', 'author', 'post')
    search_fields = ('text',)
    list_filter = ('pub_date',)


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    """Представляет модель Follow в интерфейсе администратора."""

    list_display = ('user', 'author', )


admin.site.register(Group)
