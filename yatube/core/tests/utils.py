"""Базовые классы для наборов тестов в других приложениях."""
from http import HTTPStatus

from django.test import TestCase
from django.core.cache import cache


class URLTests(TestCase):
    """
    Набор функций, проверяющих различные реакции при обращении по заданным URL.
    """

    def setUp(self):
        super().setUp()
        cache.clear()

    def _test_response_is_ok(self, urls, client):
        """Запросы к заданным URL успешны?"""
        self._test_response_status(urls, client, HTTPStatus.OK)

    def _test_response_is_redirection(self, urls, client):
        """Запросы к заданным URL были перенаправлены?"""
        self._test_response_status(urls, client, HTTPStatus.FOUND)

    def _test_response_is_not_found(self, urls, client):
        """Страницы по заданным URL не найдены?"""
        self._test_response_status(urls, client, HTTPStatus.NOT_FOUND)

    def _test_response_status(self, urls, client, status_code):
        """Запросы к заданным URL вернули требуемый код завершения?"""
        for url in urls:
            with self.subTest(url=url):
                response = client.get(url)
                self.assertEqual(response.status_code, status_code)

    def _test_redirection(self, urls, client, redirection_rule):
        """Запросы к заданным URL были перенаправлены в нужные места?"""
        for url in urls:
            with self.subTest(url=url):
                response = client.get(url)
                self.assertRedirects(response, redirection_rule(url))

    def _test_templates(self, urls, client):
        """Страницы по заданным URL используют надлежащие шаблоны?"""
        for url, template in urls.items():
            with self.subTest(url=url):
                response = client.get(url)
                self.assertTemplateUsed(response, template)


class BaseSimpleURLTestCase(URLTests):
    """Заготовка набора тестов для простого приложения, проверяющих различные
    реакции при обращении по заданным URL.
    """

    @classmethod
    def get_urls(cls):
        """Возвращает словарь {'url':'template'} для всех страниц приложения.
        """
        raise NotImplementedError

    @classmethod
    def get_nonexistent_urls(cls):
        """Возвращает перечень (iterable) несуществующих URL для проверки."""
        raise NotImplementedError

    def _test_response_is_ok(self):
        """Запросы к URL из списка успешны?"""
        urls = self.get_urls()
        super()._test_response_is_ok(urls, self.client)

    def _test_response_is_not_found(self):
        """Страницы с URL из списка не найдены?"""
        urls = self.get_nonexistent_urls()
        super()._test_response_is_not_found(urls, self.client)

    def _test_templates(self):
        """Страницы с URL из списка используют надлежащие шаблоны?"""
        urls = self.get_urls()
        super()._test_templates(urls, self.client)
