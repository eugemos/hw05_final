"""Тесты для проверки URL приложения users."""
from core.tests.utils import BaseSimpleURLTestCase


class URLTestCase(BaseSimpleURLTestCase):
    """Набор тестов для проверки URL приложения users."""

    def test_all_pages_accessible(self):
        """Все страницы приложения доступны и используют надлежащие шаблоны?"""
        urls = {
            '/auth/login/': 'users/login.html',
            '/auth/logout/': 'users/logged_out.html',
            '/auth/signup/': 'users/signup.html',
        }
        self._test_pages_accessible(urls)

    def test_nonexistent_pages_unaccessible(self):
        """Несуществующие страницы недоступны?"""
        urls = ('/auth/nonexistent_page/',)
        self._test_pages_inaccessible(urls)
