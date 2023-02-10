"""Тесты для проверки URL приложения posts."""
from django.test import Client
from django.urls import reverse

from core.tests.utils import URLTests
from users.models import User
from posts.models import Post, Group


class URLTestCase(URLTests):
    """Набор тестов для проверки URL приложения posts."""

    @classmethod
    def setUpClass(cls):
        """Создаёт фикстуры для всего набора тестов."""
        super().setUpClass()
        cls.user = User.objects.create_user(username='test-user')
        cls.author = User.objects.create_user(username='test-author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test',
            description='Группа записей для тестирования',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            group=cls.group,
            text='Запись для тестирования.',
        )
        cls.url_of_add_comment = f'/posts/{cls.post.pk}/comment/'

    @classmethod
    def get_urls_for_all(cls):
        """Возвращает словарь {'url':'template'} для страниц приложения,
        которые должны быть доступны без авторизации.
        """
        slug = cls.group.slug
        username = cls.user.username
        post_id = cls.post.pk
        return {
            '/': 'posts/index.html',
            f'/group/{slug}/': 'posts/group_list.html',
            f'/profile/{username}/': 'posts/profile.html',
            f'/posts/{post_id}/': 'posts/post_detail.html',
        }

    @classmethod
    def get_urls_for_authorized(cls):
        """Возвращает словарь {'url':'template'} для страниц приложения,
        которые должны быть доступны только авторизованным клиентам,
        но без требования быть автором поста (кроме 'add_comment').
        """
        return {
            '/create/': 'posts/create_post.html',
        }

    @classmethod
    def get_urls_for_author(cls):
        """Возвращает словарь {'url':'template'} для страниц приложения,
        которые должны быть доступны только автору поста.
        """
        post_id = cls.post.pk
        return {
            f'/posts/{post_id}/edit/': 'posts/create_post.html',
        }

    @classmethod
    def get_nonexistent_urls(cls):
        """Возвращает кортеж несуществующих URL для проверки."""
        nonexistent_post_id = cls.post.pk + 1
        return (
            '/nonexistent_page/',
            '/group/nonexistent_slug/',
            '/profile/nonexistent_username/',
            f'/posts/{nonexistent_post_id}/',
            f'/posts/{nonexistent_post_id}/edit/',
            f'/posts/{nonexistent_post_id}/comment/',
        )

    @classmethod
    def get_redirection_urls_for_not_author(cls):
        """Возвращает словарь {'url':'redirect url'} для страниц приложения,
        которые должны быть доступны только автору поста.
        """
        post_id = cls.post.pk
        return {
            reverse('posts:post_edit', args=[post_id]):
                reverse('posts:post_detail', args=[post_id]),
        }

    def setUp(self):
        """Создаёт фикстуры для отдельного теста."""
        super().setUp()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.author_client = Client()
        self.author_client.force_login(self.author)

    def test_pages_for_all_accessible_for_unauthorized_client(self):
        """Страницы приложения, которые должны быть доступны без авторизации,
        доступны неавторизованному клиенту?
        """
        urls = self.get_urls_for_all()
        self._test_response_is_ok(urls, self.client)

    def test_pages_not_for_all_redirect_unauthorized_client_properly(self):
        """Страницы приложения, которые должны быть доступны только
        авторизованным клиентам (включая 'add_comment'), перенаправляют
        неавторизованного клиента на надлежащий URL?
        """
        urls = self.get_urls_for_authorized()
        urls.update(self.get_urls_for_author())
        urls.update({self.url_of_add_comment: None})
        self._test_redirection(
            urls, self.client,
            lambda url: reverse('users:login') + f'?next={url}'
        )

    def test_pages_for_authorized_accessible_for_authorized_client(self):
        """Страницы приложения, которые должны быть доступны только
        авторизованным клиентам, но без требования быть автором поста
        (кроме 'add_comment'), доступны авторизованному клиенту?
        """
        urls = self.get_urls_for_authorized()
        self._test_response_is_ok(urls, self.authorized_client)

    def test_add_comment_page_redirects_authorized_client_properly(self):
        """Страница 'add_comment' перенаправляет авторизованного клиента
        на надлежащий URL?
        """
        urls = (self.url_of_add_comment,)
        self._test_redirection(
            urls, self.authorized_client,
            lambda url: reverse('posts:post_detail', args=[self.post.pk])
        )

    def test_pages_for_author_redirect_authorized_client_properly(self):
        """Cтраницы приложения, которые должны быть доступны только автору
        поста, перенаправляют авторизованного клиента, не являющегося автором
        поста, на надлежащий URL?
        """
        urls = self.get_urls_for_author()
        redirection_urls = self.get_redirection_urls_for_not_author()
        self._test_redirection(urls, self.authorized_client,
                               lambda url: redirection_urls[url])

    def test_pages_for_author_accessible_for_author(self):
        """Cтраницы приложения, которые должны быть доступны только автору
        поста, доступны автору поста?
        """
        urls = self.get_urls_for_author()
        self._test_response_is_ok(urls, self.author_client)

    def test_nonexistent_pages_unaccessible(self):
        """Несуществующие страницы недоступны?"""
        urls = self.get_nonexistent_urls()
        self._test_response_is_not_found(urls, self.author_client)

    def test_all_pages_use_proper_templates(self):
        """Все страницы приложения используют надлежащие шаблоны?"""
        urls = self.get_urls_for_all()
        urls.update(self.get_urls_for_authorized())
        urls.update(self.get_urls_for_author())
        self._test_templates(urls, self.author_client)
