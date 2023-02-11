"""Тесты для проверки моделей приложения posts."""
from users.models import User
from posts.models import Group, Post, Comment
from posts.constants import (NUMBER_OF_POST_CHARS_DISPLAYED,
                             NUMBER_OF_COMMENT_CHARS_DISPLAYED)
from core.tests.utils import BaseTestCase


class ModelTests(BaseTestCase):
    """Набор функций для проверки моделей."""

    def _test_obj_fields_have_required_property_values(
        self, obj, property, rules
    ):
        """
        Свойства property полей объекта obj имеют значения, заданные в rules?
        """
        for field, expected_value in rules.items():
            with self.subTest(field=field):
                self.assertEqual(
                    getattr(obj._meta.get_field(field), property),
                    expected_value
                )


class GroupModelTestCase(ModelTests):
    """Набор тестов для модели posts.Group."""

    @classmethod
    def setUpClass(cls):
        """Создаёт фикстуры для всего набора тестов."""
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test',
            description='Группа записей для тестирования'
        )

    def test_str_method_works_properly(self):
        """Метод __str__ работает правильно?"""
        right_out = self.group.title
        self.assertEqual(str(self.group), right_out)

    def test_verbose_name_properties_have_required_values(self):
        """Свойства verbose_name полей модели имеют надлежащие значения?"""
        verbose_names = {
            'title': 'Название',
            'slug': 'Идентификатор',
            'description': 'Описание',
        }
        self._test_obj_fields_have_required_property_values(
            self.group, 'verbose_name', verbose_names
        )


class PostModelTestCase(ModelTests):
    """Набор тестов для модели posts.Post."""

    @classmethod
    def setUpClass(cls):
        """Создаёт фикстуры для всего набора тестов."""
        super().setUpClass()
        user = User.objects.create_user(username='auth')
        group = Group.objects.create(
            title='Тестовая группа',
            slug='test',
            description='Группа записей для тестирования',
        )
        cls.post = Post.objects.create(
            author=user,
            group=group,
            text='Запись для тестирования.',
        )

    def test_str_method_works_properly(self):
        """Метод __str__ работает правильно?"""
        right_out = self.post.text[:NUMBER_OF_POST_CHARS_DISPLAYED]
        self.assertEqual(str(self.post), right_out)

    def test_verbose_name_properties_have_required_values(self):
        """Свойства verbose_name полей модели имеют надлежащие значения?"""
        verbose_names = {
            'text': 'Текст записи',
            'pub_date': 'Опубликовано',
            'author': 'Автор',
            'group': 'Группа',
            'image': 'Иллюстрация'
        }
        self._test_obj_fields_have_required_property_values(
            self.post, 'verbose_name', verbose_names
        )

    def test_help_text_properties_have_required_values(self):
        """Свойства help_text полей модели имеют надлежащие значения?"""
        help_texts = {
            'text': 'Введите текст записи',
            'group': 'Группа, к которой будет относиться запись',
            'image': 'Можно загрузить файл с иллюстрацией',
        }
        self._test_obj_fields_have_required_property_values(
            self.post, 'help_text', help_texts
        )


class CommentModelTestCase(ModelTests):
    """Набор тестов для модели posts.Comment."""

    @classmethod
    def setUpClass(cls):
        """Создаёт фикстуры для всего набора тестов."""
        super().setUpClass()
        author = User.objects.create_user(username='author')
        user = User.objects.create_user(username='user')
        post = Post.objects.create(
            author=author,
            group=None,
            text='Запись для тестирования.',
        )
        cls.comment = Comment.objects.create(
            author=user,
            post=post,
            text='Комментарий для тестирования.',
        )

    def test_str_method_works_properly(self):
        """Метод __str__ работает правильно?"""
        right_out = self.comment.text[:NUMBER_OF_COMMENT_CHARS_DISPLAYED]
        self.assertEqual(str(self.comment), right_out)

    def test_verbose_name_properties_have_required_values(self):
        """Свойства verbose_name полей модели имеют надлежащие значения?"""
        verbose_names = {
            'text': 'Текст комментария',
            'pub_date': 'Опубликовано',
            'author': 'Автор',
        }
        self._test_obj_fields_have_required_property_values(
            self.comment, 'verbose_name', verbose_names
        )

    def test_help_text_properties_have_required_values(self):
        """Свойства help_text полей модели имеют надлежащие значения?"""
        help_texts = {
            'text': 'Введите текст комментария',
        }
        self._test_obj_fields_have_required_property_values(
            self.comment, 'help_text', help_texts
        )
