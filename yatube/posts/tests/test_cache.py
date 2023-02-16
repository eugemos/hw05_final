"""Тесты для проверки кэширования в приложении posts."""
from django.urls import reverse
from django.core.cache import cache

from users.models import User
from posts.models import Post
from core.tests.utils import BaseTestCase


class CacheTestCase(BaseTestCase):
    """Набор тестов для проверки кеширования страниц."""

    @classmethod
    def setUpClass(cls):
        """Создаёт фикстуры для всего набора тестов."""
        super().setUpClass()
        cls.author = User.objects.create_user(username='test-author')
        cls.post = Post.objects.create(
            author=cls.author,
            group=None,
            text='Тестовая запись.',
        )
        cls.post_other = Post.objects.create(
            author=cls.author,
            group=None,
            text='Другая запись.',
        )

    def test_cach_works_properly(self):
        """Кэш работает правильно?"""
        old_content = self.client.get(reverse('posts:index')).content
        Post.objects.filter(pk=self.post_other.pk).delete()
        new_content = self.client.get(reverse('posts:index')).content
        self.assertEqual(old_content, new_content)
        cache.clear()
        new_content = self.client.get(reverse('posts:index')).content
        self.assertNotEqual(old_content, new_content)
