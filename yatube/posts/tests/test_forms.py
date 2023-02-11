"""Тесты для проверки форм приложения posts."""
from django.test import Client

from posts.models import Post, Group
from users.models import User
from .utils import BaseTestCaseForPostFormWork


class PostFormTestCase(BaseTestCaseForPostFormWork):
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
