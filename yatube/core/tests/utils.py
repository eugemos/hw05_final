"""Базовые классы для наборов тестов в других приложениях."""
from functools import partial
from http import HTTPStatus

from django.test import TestCase
from django.core.cache import cache
from django.urls import reverse


class BaseTestCase(TestCase):
    """Базовый класс для всех наборов теcтов в проекте Yatube."""

    def setUp(self):
        """Создаёт фикстуры для отдельного теста."""
        super().setUp()
        cache.clear()


class URLTests(BaseTestCase):
    """Набор функций для проверки реакций при обращении к URL."""

    def _test_page_accessible(self, url, client, template):
        """Страница доступна и использует надлежащий шаблон?"""
        response = client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, template)

    def _test_page_inaccessible(self, url, client):
        """Страница недоступна?"""
        response = client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def _test_page_redirects(self, url, client, redirection_url=None):
        """Страница выполняет перенаправление на требуемый URL?"""
        response = client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        if redirection_url:
            self.assertRedirects(response, redirection_url)

    def _test_page_redirects_to_login(self, url, client):
        """Страница выполняет перенаправление на страницу регистрации?"""
        response = client.get(url)
        self.assertRedirects(response, reverse('users:login') + f'?next={url}')


class BaseRuledURLTestCase(URLTests):
    """Базовый класс для набора тестов, проверяющего реакции при обращении
    к URL в соответствии с заданными правилами.
    """

    def must_be_accessible(self, client, template):
        """Возвращает тест, проверяющий, что страница доступна и использует
        надлежащий шаблон.
        """
        test = partial(self._test_page_accessible,
                       client=client, template=template)
        test.__doc__ = 'Страница доступна?'
        return test

    def must_be_inaccessible(self, client):
        """Возвращает тест, проверяющий, что страница недоступна."""
        test = partial(self._test_page_inaccessible, client=client)
        test.__doc__ = 'Страница недоступна?'
        return test

    def must_redirect(self, client, redirection_url):
        """Возвращает тест, проверяющий, что страница выполняет
        перенаправление.
        """
        test = partial(self._test_page_redirects,
                       client=client, redirection_url=redirection_url)
        test.__doc__ = f'Страница перенаправляет на {redirection_url}?'
        return test

    def must_redirect_to_login(self, client):
        """Возвращает тест, проверяющий, что страница выполняет
        перенаправление на страницу регистрации.
        """
        test = partial(self._test_page_redirects_to_login, client=client)
        test.__doc__ = 'Страница перенаправляет на login?'
        return test

    def execute(self, rules: dict):
        """Выполняет тестирование в соответствии с набором правил."""
        for url, tests in rules.items():
            with self.subTest(url=url):
                for test in tests:
                    with self.subTest(test=test.__doc__):
                        test(url)


class BaseSimpleURLTestCase(URLTests):
    """Базовый класс для набора тестов, проверяющих реакции при обращении к URL
    в простом приложении.
    """

    def _test_pages_accessible(self, urls: dict, client=None):
        """Страницы доступны и используют надлежащие шаблоны?"""
        for url, template in urls.items():
            with self.subTest(url=url):
                self._test_page_accessible(
                    url, client or self.client, template
                )

    def _test_pages_redirect(self, urls: dict, client=None):
        """Страницы выполняют перенаправление на требуемые URL?"""
        for url, redirect_url in urls.items():
            with self.subTest(url=url):
                self._test_page_redirects(
                    url, client or self.client, redirect_url
                )

    def _test_pages_inaccessible(self, urls, client=None):
        """Страницы недоступны?"""
        for url in urls:
            with self.subTest(url=url):
                self._test_page_inaccessible(url, client or self.client)
