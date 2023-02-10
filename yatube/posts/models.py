from django.db import models

from users.models import User
from .constants import (NUMBER_OF_POST_CHARS_DISPLAYED,
                        NUMBER_OF_COMMENT_CHARS_DISPLAYED)


class Group(models.Model):
    """Представляет группу записей."""

    title = models.CharField('Название', max_length=200)
    slug = models.SlugField('Идентификатор', unique=True)
    description = models.TextField('Описание')

    def __str__(self):
        return self.title


class Published(models.Model):
    """Представляет нечто опубликованное (ABC)."""

    pub_date = models.DateTimeField('Опубликовано', auto_now_add=True)

    class Meta:
        abstract = True
        ordering = ['-pub_date']


class Post(Published):
    """Представляет опубликованную запись."""

    text = models.TextField(
        'Текст записи',
        help_text='Введите текст записи',
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        related_name='posts',
        on_delete=models.CASCADE,
    )
    group = models.ForeignKey(
        Group,
        verbose_name='Группа',
        help_text='Группа, к которой будет относиться запись',
        related_name='posts',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    image = models.ImageField(
        'Иллюстрация',
        help_text='Можно загрузить файл с иллюстрацией',
        upload_to='posts/',
        blank=True,
    )

    def __str__(self):
        return self.text[:NUMBER_OF_POST_CHARS_DISPLAYED]


class Comment(Published):
    """Представляет комментарий к записи."""

    text = models.TextField(
        'Текст комментария',
        help_text='Введите текст комментария',
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        related_name='comments',
        on_delete=models.CASCADE,
    )
    post = models.ForeignKey(
        Post,
        verbose_name='Запись',
        related_name='comments',
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.text[:NUMBER_OF_COMMENT_CHARS_DISPLAYED]
