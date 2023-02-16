"""Тесты для проверки view-функций приложения posts."""
from django.test import Client
from django.urls import reverse

from core.tests.utils import BaseSimpleURLTestCase, BaseTestCase
from users.models import User
from posts.models import Post, Group, Follow
from posts.constants import (NUMBER_OF_POSTS_ON_MAIN_PAGE,
                             NUMBER_OF_POSTS_ON_GROUP_PAGE,
                             NUMBER_OF_POSTS_ON_USER_PAGE,
                             )
import posts.tests.utils as utils


class PageNamesTestCase(BaseSimpleURLTestCase):
    """Набор тестов для проверки имён страниц приложения posts."""

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

    def setUp(self):
        """Создаёт фикстуры для отдельного теста."""
        super().setUp()
        self.author_client = Client()
        self.author_client.force_login(self.author)

    def test_view_pages_accessible_by_name(self):
        """Все view-страницы приложения доступны по имени и используют
        надлежащие шаблоны?
        """
        slug = self.group.slug
        username = self.user.username
        post_id = self.post.pk
        urls = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:follow_index'): 'posts/follow.html',
            reverse('posts:group_list', args=[slug]):
                'posts/group_list.html',
            reverse('posts:profile', args=[username]):
                'posts/profile.html',
            reverse('posts:post_create'):
                'posts/create_post.html',
            reverse('posts:post_detail', args=[post_id]):
                'posts/post_detail.html',
            reverse('posts:post_edit', args=[post_id]):
                'posts/create_post.html',
        }
        self._test_pages_accessible(urls, self.author_client)

    def test_action_pages_accessible_by_name(self):
        """Все action-страницы приложения доступны по имени?"""
        post_id = self.post.pk
        username = self.author.username
        urls = {
            reverse('posts:add_comment', args=[post_id]): None,
            reverse('posts:profile_follow', args=[username]): None,
            reverse('posts:profile_unfollow', args=[username]): None,
        }
        self._test_pages_redirect(urls, self.author_client)


class IndexPageTestCase(utils.BaseTestCaseForPageWithPaginator):
    """Набор тестов для страницы posts:index."""

    NUMBER_OF_POSTS_ON_FIRST_PAGE = NUMBER_OF_POSTS_ON_MAIN_PAGE

    @classmethod
    def setUpClass(cls):
        """Создаёт фикстуры для всего набора тестов."""
        super().setUpClass()
        cls.url = reverse('posts:index')


class GroupListPageTestCase(utils.BaseTestCaseForPageWithPaginator):
    """Набор тестов для страницы posts:group_list."""

    NUMBER_OF_POSTS_ON_FIRST_PAGE = NUMBER_OF_POSTS_ON_GROUP_PAGE

    @classmethod
    def setUpClass(cls):
        """Создаёт фикстуры для всего набора тестов."""
        super().setUpClass()
        cls.url = reverse('posts:group_list', args=[cls.group.slug])
        Post.objects.create(
            author=cls.author,
            group=None,
            text='Ещё одна запись.',
        )

    def test_group_of_context_is_correct(self):
        """В контекст шаблона передано верное значение group?"""
        response = self.client.get(self.url)
        group_of_context = response.context['group']
        self.assertEqual(group_of_context, self.group)


class ProfilePageTestCase(utils.BaseTestCaseForPageWithPaginator):
    """Набор тестов для страницы posts:profile."""

    NUMBER_OF_POSTS_ON_FIRST_PAGE = NUMBER_OF_POSTS_ON_USER_PAGE

    @classmethod
    def setUpClass(cls):
        """Создаёт фикстуры для всего набора тестов."""
        super().setUpClass()
        cls.author_other = User.objects.create_user(username='other-author')
        cls.url = reverse('posts:profile', args=[cls.author.username])
        Post.objects.create(
            author=cls.author_other,
            group=None,
            text='Ещё одна запись.',
        )

    def test_author_of_context_is_correct(self):
        """В контекст шаблона передано верное значение author?"""
        response = self.client.get(self.url)
        author_of_context = response.context['author']
        self.assertEqual(author_of_context, self.author)

    def test_following_of_context_is_correct(self):
        """В контекст шаблона передаётся верное значение following?"""
        user = User.objects.create_user(username='test-user')
        Follow.objects.create(user=user, author=self.author)
        url_other = reverse('posts:profile', args=[self.author_other.username])
        authorized_client = Client()
        authorized_client.force_login(user)

        with self.subTest(test='Неавторизованный пользователь.'):
            self._test_following_of_context_has_expected_value(
                self.url, self.client, False
            )

        with self.subTest(test='Авторизованный подписанный пользователь.'):
            self._test_following_of_context_has_expected_value(
                self.url, authorized_client, True
            )

        with self.subTest(test='Авторизованный неподписанный пользователь.'):
            self._test_following_of_context_has_expected_value(
                url_other, authorized_client, False
            )

    def _test_following_of_context_has_expected_value(
        self, url, client, exp_following
    ):
        """В контекст шаблона передаётся ожидаемое значение following?"""
        response = client.get(url)
        following_of_context = response.context['following']
        self.assertEqual(following_of_context, exp_following)


class PostDetailPageTestCase(utils.BaseTestCaseWithUploadedFiles):
    """Набор тестов для страницы posts:post_detail."""

    @classmethod
    def setUpClass(cls):
        """Создаёт фикстуры для всего набора тестов."""
        super().setUpClass()
        cls.author = User.objects.create_user(username='test-author')
        cls.author_other = User.objects.create_user(username='other-author')
        cls.expected_post = Post.objects.create(
            author=cls.author,
            group=None,
            text='Запись.',
            image=cls.create_uploaded_gif('test.gif')
        )
        cls.post_other = Post.objects.create(
            author=cls.author_other,
            group=None,
            text='Ещё одна запись.',
        )
        cls.url = reverse('posts:post_detail', args=[cls.expected_post.pk])

    def test_page_contains_proper_post(self):
        """Страница содержит надлежащую запись?"""
        self.response = self.client.get(self.url)
        actual_post = self.response.context['post']
        self._test_posts_are_equal(self.expected_post, actual_post)

    def _test_posts_are_equal(self, post1, post2):
        """Записи имеют идентичные поля?"""
        self.assertEqual(post1.pk, post2.pk)
        self.assertEqual(post1.group, post2.group)
        self.assertEqual(post1.author, post2.author)
        self.assertEqual(post1.text, post2.text)
        self.assertEqual(post1.image.name, post2.image.name)
        self._test_files_are_equal(post1.image, post2.image)


class PostCreatePageTestCase(utils.BaseTestCaseForPostFormView):
    """Набор тестов для страницы posts:post_create."""

    @classmethod
    def setUpClass(cls):
        """Создаёт фикстуры для всего набора тестов."""
        super().setUpClass()
        cls.url = reverse('posts:post_create')


class PostEditPageTestCase(utils.BaseTestCaseForPostFormView,
                           utils.BaseTestCaseWithUploadedFiles):
    """Набор тестов для страницы posts:post_edit."""

    @classmethod
    def setUpClass(cls):
        """Создаёт фикстуры для всего набора тестов."""
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test',
            description='Группа записей для тестирования',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            group=cls.group,
            text='Запись.',
            image=cls.create_uploaded_gif('test.gif')
        )
        cls.url = reverse('posts:post_edit', args=[cls.post.pk])

    def test_form_on_page_contains_proper_data(self):
        """Форма на странице содержит надлежащие данные?"""
        response = self.client.get(self.url)
        form_fields = {
            'text': self.post.text,
            'group': self.post.group.pk,
            'image': self.post.image,
        }

        for field_name, expected_value in form_fields.items():
            with self.subTest(field=field_name):
                field_value = response.context['form'][field_name].value()
                self.assertEqual(field_value, expected_value)


class NewPostCreationTestCase(utils.BaseTestCaseForPostFormWork):
    """Набор тестов для проверки правильности реакции приложения posts
    на создание новой записи.
    """

    @classmethod
    def setUpClass(cls):
        """Создаёт фикстуры для всего набора тестов."""
        super().setUpClass()
        cls.author = User.objects.create_user(username='test-author')
        cls.author_other = User.objects.create_user(username='other-author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test',
            description='Тестовая группа записей',
        )
        cls.group_other = Group.objects.create(
            title='Другая группа',
            slug='test-other',
            description='Другая группа записей',
        )
        cls.user = User.objects.create_user(username='test-user')
        cls.user_follower = User.objects.create_user(username='follower-user')
        Follow.objects.create(author=cls.author, user=cls.user_follower)

    def setUp(self):
        """Создаёт фикстуры для отдельного теста."""
        super().setUp()
        author_client = Client()
        author_client.force_login(self.author)
        form_data = {
            'text': 'Новая запись.',
            'group': self.group.pk,
            'image': self.create_uploaded_gif('small.gif'),
        }
        self.post = self.create_new_post_with_form_and_get_it(form_data,
                                                              author_client)

    def test_post_appeared_on_pages_intended_for_it(self):
        """Запись появилась на надлежащих страницах?"""
        urls = (
            reverse('posts:index'),
            reverse('posts:follow_index'),
            reverse('posts:group_list', args=[self.group.slug]),
            reverse('posts:profile', args=[self.author.username]),
        )
        self.client.force_login(self.user_follower)
        for url in urls:
            with self.subTest(page=url):
                self._test_post_appeared_on_page(url, self.post)

    def test_post_not_appeared_on_pages_not_intended_for_it(self):
        """Запись не появилась на ненадлежащих страницах?"""
        urls = (
            reverse('posts:follow_index'),
            reverse('posts:group_list', args=[self.group_other.slug]),
            reverse('posts:profile', args=[self.author_other.username]),
        )
        self.client.force_login(self.user)
        for url in urls:
            with self.subTest(page=url):
                self._test_post_not_appeared_on_page(url, self.post)

    def _test_post_appeared_on_page(self, url, post):
        """Запись появилась на заданной странице?"""
        response = self.client.get(url)
        page_posts = response.context['page_obj'].paginator.object_list
        self.assertIn(post, page_posts)

    def _test_post_not_appeared_on_page(self, url, post):
        """Запись не появилась на заданной странице?"""
        response = self.client.get(url)
        page_posts = response.context['page_obj'].paginator.object_list
        self.assertNotIn(post, page_posts)


class NewCommentCreationTestCase(utils.BaseTestCaseForCommentFormWork):
    """Набор тестов для проверки правильности реакции приложения posts
    на добавление нового комментария к записи.
    """

    @classmethod
    def setUpClass(cls):
        """Создаёт фикстуры для всего набора тестов."""
        super().setUpClass()
        author = User.objects.create_user(username='test-author')
        cls.user = User.objects.create_user(username='test-user')
        cls.post = Post.objects.create(
            author=author,
            group=None,
            text='Запись.',
        )
        cls.post_other = Post.objects.create(
            author=author,
            group=None,
            text='Ещё одна запись.',
        )

    def setUp(self):
        """Создаёт фикстуры для отдельного теста."""
        super().setUp()
        authorized_client = Client()
        authorized_client.force_login(self.user)
        form_data = {
            'text': 'Новая запись.',
        }
        self.comment = self.create_new_comment_with_form_and_get_it(
            self.post.pk, form_data, authorized_client
        )

    def test_comment_appeared_on_pages_intended_for_it(self):
        """Комментарий появился на надлежащих страницах?"""
        urls = (
            reverse('posts:post_detail', args=[self.post.pk]),
        )
        for url in urls:
            with self.subTest(page=url):
                self._test_comment_appeared_on_page(url, self.comment)

    def test_comment_not_appeared_on_pages_not_intended_for_it(self):
        """Комментарий не появился на ненадлежащих страницах?"""
        urls = (
            reverse('posts:post_detail', args=[self.post_other.pk]),
        )
        for url in urls:
            with self.subTest(page=url):
                self._test_comment_not_appeared_on_page(url, self.comment)

    def _test_comment_appeared_on_page(self, url, comment):
        """Комментарий появился на заданной странице?"""
        response = self.client.get(url)
        page_comments = response.context['comments']
        self.assertIn(comment, page_comments)

    def _test_comment_not_appeared_on_page(self, url, comment):
        """Комментарий не появился на заданной странице?"""
        response = self.client.get(url)
        page_comments = response.context['comments']
        self.assertNotIn(comment, page_comments)


class FollowUnfollowTestCase(BaseTestCase):
    """Набор тестов для проверки возможности подписки/отписки."""

    @classmethod
    def setUpClass(cls):
        """Создаёт фикстуры для всего набора тестов."""
        super().setUpClass()
        cls.author = User.objects.create_user(username='test-author')
        cls.user = User.objects.create_user(username='test-user')

    def setUp(self):
        """Создаёт фикстуры для отдельного теста."""
        super().setUp()
        self.client.force_login(self.user)

    def test_authorized_user_can_follow_author(self):
        """Авторизованный пользователь может подписаться на автора?"""
        self.assertFalse(
            Follow.objects.filter(user=self.user, author=self.author).exists()
        )
        self.client.get(
            reverse('posts:profile_follow', args=[self.author.username])
        )
        self.assertTrue(
            Follow.objects.filter(user=self.user, author=self.author).exists()
        )

    def test_authorized_user_can_unfollow_author(self):
        """Авторизованный пользователь может отменить подписку на автора?"""
        Follow.objects.create(user=self.user, author=self.author)
        self.assertTrue(
            Follow.objects.filter(user=self.user, author=self.author).exists()
        )
        self.client.get(
            reverse('posts:profile_unfollow', args=[self.author.username])
        )
        self.assertFalse(
            Follow.objects.filter(user=self.user, author=self.author).exists()
        )
