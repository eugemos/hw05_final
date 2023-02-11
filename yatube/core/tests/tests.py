"""Тесты для проверки функционирования приложения core."""
from http import HTTPStatus

from django.urls import reverse
from django.core.cache import cache

from users.models import User
from posts.models import Post
from core.tests.utils import BaseTestCase


class CacheTestCase(BaseTestCase):
    """Набор тестов для проверки кеширования."""

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
        old_posts_count = self.get_number_of_posts_on_main_page()
        Post.objects.filter(pk=self.post_other.pk).delete()
        new_posts_count = self.get_number_of_posts_on_main_page()
        self.assertEqual(old_posts_count, new_posts_count)
        cache.clear()
        new_posts_count = self.get_number_of_posts_on_main_page()
        self.assertEqual(old_posts_count - 1, new_posts_count)

    def get_number_of_posts_on_main_page(self):
        """Возвращает количество записей, отображаемых на главной странице."""
        response = self.client.get(reverse('posts:index'))
        return response.content.count(b'<article>')


class CustomError404PageTestCase(BaseTestCase):
    """Тест для проверки работы кастомной страницы ошибки 404."""

    def test_custom_error_404_page(self):
        """При возникновении ошибки 404 выдаётся кастомная страница?"""
        response = self.client.get('/nonexistent_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, 'core/404.html')
