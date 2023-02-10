"""Тесты для проверки view-функций приложения users."""
from django.urls import reverse

from core.tests.utils import BaseSimpleURLTestCase


class PageNamesTestCase(BaseSimpleURLTestCase):
    """Набор тестов для проверки имён страниц приложения users."""

    @classmethod
    def get_urls(cls):
        """Возвращает словарь {'url':'template'} для всех страниц приложения.
        """
        return {
            reverse('users:login'): 'users/login.html',
            reverse('users:logout'): 'users/logged_out.html',
            reverse('users:signup'): 'users/signup.html',
        }

    def test_all_pages_accessible_by_name(self):
        """Все страницы приложения доступны по имени?"""
        self._test_response_is_ok()

    def test_all_page_names_correspond_to_proper_templates(self):
        """Всем именам страниц приложения сопоставлены надлежащие шаблоны?"""
        self._test_templates()
