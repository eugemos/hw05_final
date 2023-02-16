"""Тесты для проверки функционирования приложения core."""
from http import HTTPStatus

from core.tests.utils import BaseTestCase


class CustomError404PageTestCase(BaseTestCase):
    """Тест для проверки работы кастомной страницы ошибки 404."""

    def test_custom_error_404_page(self):
        """При возникновении ошибки 404 выдаётся кастомная страница?"""
        response = self.client.get('/nonexistent_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, 'core/404.html')
