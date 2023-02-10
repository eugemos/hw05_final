"""Тесты для проверки приложения about."""
from django.urls import reverse

from core.tests.utils import BaseSimpleURLTestCase


class URLTestCase(BaseSimpleURLTestCase):
    """Набор тестов для проверки URL приложения about."""

    @classmethod
    def get_urls(cls):
        """Возвращает словарь {'url':'template'} для всех страниц приложения.
        """
        return {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html',
        }

    @classmethod
    def get_nonexistent_urls(cls):
        """Возвращает кортеж несуществующих URL для проверки."""
        return (
            '/about/unexisted_page/',
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


class URLNamesTestCase(BaseSimpleURLTestCase):
    """Набор тестов для проверки имён страниц приложения about."""

    @classmethod
    def get_urls(cls):
        """Возвращает словарь {'url':'template'} для всех страниц приложения.
        """
        return {
            reverse('about:author'): 'about/author.html',
            reverse('about:tech'): 'about/tech.html',
        }

    def test_all_pages_accessible_by_name(self):
        """Все страницы приложения доступны по имени?"""
        self._test_response_is_ok()

    def test_all_page_names_correspond_to_proper_templates(self):
        """Всем именам страниц приложения сопоставлены надлежащие шаблоны?"""
        self._test_templates()
