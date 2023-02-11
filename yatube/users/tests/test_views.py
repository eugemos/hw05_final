"""Тесты для проверки view-функций приложения users."""
from django.urls import reverse

from core.tests.utils import BaseSimpleURLTestCase


class PageNamesTestCase(BaseSimpleURLTestCase):
    """Набор тестов для проверки имён страниц приложения users."""

    def test_all_pages_accessible_by_name(self):
        """Все страницы приложения доступны по имени и используют надлежащие
        шаблоны?
        """
        urls = {
            reverse('users:login'): 'users/login.html',
            reverse('users:logout'): 'users/logged_out.html',
            reverse('users:signup'): 'users/signup.html',
        }
        self._test_pages_accessible(urls)
