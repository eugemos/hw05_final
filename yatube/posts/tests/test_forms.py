"""Тесты для проверки форм приложения posts."""
from django.test import Client, TestCase

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

    # def create_new_post_with_form_and_get_it(self, form_data, client):
    #     """Создаёт новую запись с помощью формы и возвращает её."""
    #     old_post_ids = (post.pk for post in Post.objects.all())
    #     response = client.post(
    #         reverse('posts:post_create'),
    #         data=form_data,
    #         follow=True
    #     )
    #     self.assertRedirects(
    #         response, reverse('posts:profile', args=[self.author.username])
    #     )
    #     new_posts = Post.objects.exclude(pk__in=old_post_ids)
    #     self.assertEqual(new_posts.count(), 1)
    #     return new_posts[0]

    # def change_post_with_form_and_get_it(self, post_id, form_data, client):
    #     """Изменяет запись с помощью формы и возвращает её."""
    #     old_posts_count = Post.objects.count()
    #     response = client.post(
    #         reverse('posts:post_edit', args=[post_id]),
    #         data=form_data,
    #         follow=True
    #     )
    #     self.assertRedirects(
    #         response, reverse('posts:post_detail', args=[post_id])
    #     )
    #     self.assertEqual(old_posts_count, Post.objects.count())
    #     return Post.objects.get(pk=post_id)

    # def _test_post_data_corresponds_to_data_given(self, post, *,
    #         author, text, group, image):
    #     """Значения полей записи соответствуют требуемым?"""
    #     self.assertEqual(post.author, author)
    #     self.assertEqual(post.text, text)
    #     self.assertEqual(post.group.pk, group)
    #     self.assertEqual(post.image.name, 'posts/' + image.name)
    #     self._test_files_are_equal(post.image, image)


class CommentFormTestCase(TestCase):
    """Набор тестов для проверки формы CommentForm в приложении posts."""

    @classmethod
    def setUpClass(cls):
        """Создаёт фикстуры для всего набора тестов."""
        super().setUpClass()
        cls.author = User.objects.create_user(username='test-author')
        cls.user = User.objects.create_user(username='test-user')
        cls.post = Post.objects.create(
            author=cls.author,
            group=None,
            text='Тестовая запись.',
        )

    def setUp(self):
        """Создаёт фикстуры для отдельного теста."""
        self.author_client = Client()
        self.author_client.force_login(self.author)

    # def test_valid_form_on_post_create_page_creates_new_post(self):
    #     """Валидная форма на странице post_create создаёт новую запись?"""
    #     old_post_ids = (post.pk for post in Post.objects.all())
    #     form_data = {
    #         'text': 'Новая запись.',
    #         'group': self.group.pk,
    #         'image': self.create_uploaded_gif('small.gif'),
    #     }
    #     response = self.author_client.post(
    #         reverse('posts:post_create'),
    #         data=form_data,
    #         follow=True
    #     )
    #     self.assertRedirects(
    #         response, reverse('posts:profile', args=[self.author.username])
    #     )
    #     new_posts = Post.objects.exclude(pk__in=old_post_ids)
    #     self.assertEqual(new_posts.count(), 1)
    #     self.assertEqual(new_posts[0].author, self.author)
    #     self.assertEqual(new_posts[0].text, form_data['text'])
    #     self.assertEqual(new_posts[0].group.pk, form_data['group'])
    #     self.assertEqual(new_posts[0].image.name,
    #                      'posts/' + form_data['image'].name)
    #     self._test_files_are_equal(new_posts[0].image, form_data['image'])
