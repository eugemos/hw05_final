"""Тесты для проверки форм приложения posts."""
from django.test import Client
from django.urls import reverse

from posts.models import Post, Group, Comment
from users.models import User
from posts.tests import utils


class PostFormTestCase(utils.BaseTestCaseForPostFormWork):
    """Набор тестов для проверки работы формы PostForm в приложении posts."""

    @classmethod
    def setUpClass(cls):
        """Создаёт фикстуры для всего набора тестов."""
        super().setUpClass()
        cls.author = User.objects.create_user(username='test-author')
        cls.post = Post.objects.create(
            author=cls.author,
            group=None,
            text='Старая запись.',
        )
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test',
            description='Группа записей для тестирования',
        )

    def setUp(self):
        """Создаёт фикстуры для отдельного теста."""
        self.author_client = Client()
        self.author_client.force_login(self.author)

    def tearDown(self):
        """Выполняет очистку после отдельного теста."""
        super().tearDown()
        self.clear_media_folder()

    def test_valid_form_on_post_create_page_creates_new_post(self):
        """Валидная форма на странице post_create создаёт новую запись?"""
        form_data = {
            'text': 'Новая запись.',
            'group': self.group.pk,
            'image': self.create_uploaded_gif('small.gif'),
        }
        new_post = self.create_new_post_with_form_and_get_it(
            form_data,
            self.author_client,
        )
        self._test_post_data_corresponds_to_data_given(
            new_post, author=self.author, **form_data
        )

    def test_valid_form_on_post_edit_page_changes_existing_post(self):
        """Валидная форма на странице post_edit изменяет cуществующую запись?
        """
        form_data = {
            'text': 'Изменённая запись.',
            'group': self.group.pk,
            'image': self.create_uploaded_gif('small.gif'),
        }
        post = self.change_post_with_form_and_get_it(
            self.post.pk, form_data, self.author_client
        )
        self._test_post_data_corresponds_to_data_given(
            post, author=self.author, **form_data
        )


class CommentFormTestCase(utils.BaseTestCaseForCommentFormWork):
    """Набор тестов для проверки формы CommentForm в приложении posts."""

    @classmethod
    def setUpClass(cls):
        """Создаёт фикстуры для всего набора тестов."""
        super().setUpClass()
        author = User.objects.create_user(username='test-author')
        cls.user = User.objects.create_user(username='test-user')
        cls.post = Post.objects.create(
            author=author,
            group=None,
            text='Тестовая запись.',
        )

    def setUp(self):
        """Создаёт фикстуры для отдельного теста."""
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_authorized_user_can_add_comment(self):
        """Авторизованный пользователь может добавить комментарий?"""
        form_data = {
            'text': 'Новый комментарий.',
        }
        new_comment = self.create_new_comment_with_form_and_get_it(
            self.post.pk,
            form_data,
            self.authorized_client,
        )
        self._test_comment_data_corresponds_to_data_given(
            new_comment, author=self.user, post=self.post, **form_data
        )

    def test_guest_user_can_not_add_comment(self):
        """Неавторизованный пользователь не может добавить комментарий?"""
        form_data = {
            'text': 'Новый комментарий.',
        }
        old_comment_ids = (comment.pk for comment in Comment.objects.all())
        self.client.post(
            reverse('posts:add_comment', args=[self.post.pk]),
            data=form_data,
            follow=True
        )
        new_comments = Comment.objects.exclude(pk__in=old_comment_ids)
        self.assertEqual(new_comments.count(), 0)
