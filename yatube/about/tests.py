"""Тесты для проверки приложения about."""
from django.urls import reverse

from core.tests.utils import BaseSimpleURLTestCase


class URLTestCase(BaseSimpleURLTestCase):
    """Набор тестов для проверки URL приложения about."""

    def test_all_pages_accessible(self):
        """Все страницы приложения доступны и используют надлежащие шаблоны?"""
        urls = {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html',
        }
        self._test_pages_accessible(urls)

    def test_nonexistent_pages_unaccessible(self):
        """Несуществующие страницы недоступны?"""
        urls = ('/about/nonexistent_page/',)
        self._test_pages_inaccessible(urls)


class URLNamesTestCase(BaseSimpleURLTestCase):
    """Набор тестов для проверки имён страниц приложения about."""

    def test_all_pages_accessible_by_name(self):
        """Все страницы приложения доступны по имени и используют надлежащие
        шаблоны?
        """
        urls = {
            reverse('about:author'): 'about/author.html',
            reverse('about:tech'): 'about/tech.html',
        }
        self._test_pages_accessible(urls)
