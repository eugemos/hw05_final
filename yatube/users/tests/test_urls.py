"""Тесты для проверки URL приложения users."""
from core.tests.utils import BaseSimpleURLTestCase


class URLTestCase(BaseSimpleURLTestCase):
    """Набор тестов для проверки URL приложения users."""

    @classmethod
    def get_urls(cls):
        """Возвращает словарь {'url':'template'} для всех страниц приложения.
        """
        return {
            '/auth/login/': 'users/login.html',
            '/auth/logout/': 'users/logged_out.html',
            '/auth/signup/': 'users/signup.html',
        }

    @classmethod
    def get_nonexistent_urls(cls):
        """Возвращает кортеж несуществующих URL для проверки."""
        return (
            '/auth/nonexistent_page/',
        )

    def test_all_pages_accessible(self):
        """Все страницы приложения доступны?"""
        self._test_response_is_ok()

    def test_nonexistent_pages_unaccessible(self):
        """Несуществующие страницы недоступны?"""
        self._test_response_is_not_found()

    def test_all_pages_use_proper_templates(self):
        """Все страницы приложения используют надлежащие шаблоны?"""
        self._test_templates()
