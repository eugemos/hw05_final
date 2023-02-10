from django import forms

from .models import Post, Comment


class PostForm(forms.ModelForm):
    """Представляет форму для создания/изменения записи."""

    class Meta:
        model = Post
        fields = ('text', 'group', 'image')


class CommentForm(forms.ModelForm):
    """Представляет форму для создания комментария."""

    class Meta:
        model = Comment
        fields = ('text',)
