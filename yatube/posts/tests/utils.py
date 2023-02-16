"""Базовые классы для наборов тестов приложения 'posts'."""
import shutil
import tempfile
import os.path

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.conf import settings
from django import forms
from django.urls import reverse

from posts.models import Post, Group, Comment
from users.models import User
from core.tests.utils import BaseTestCase


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class BaseTestCaseWithUploadedFiles(BaseTestCase):
    """Базовый класс для набора тестов, использующих загрузку файлов."""

    small_gif = (
        b'\x47\x49\x46\x38\x39\x61\x02\x00'
        b'\x01\x00\x80\x00\x00\x00\x00\x00'
        b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
        b'\x00\x00\x00\x2C\x00\x00\x00\x00'
        b'\x02\x00\x01\x00\x00\x02\x02\x0C'
        b'\x0A\x00\x3B'
    )

    @classmethod
    def create_uploaded_gif(cls, name):
        """Создаёт и возвращает тестовый gif-файл для загрузки."""
        return SimpleUploadedFile(
            name=name,
            content=cls.small_gif,
            content_type='image/gif'
        )

    @classmethod
    def tearDownClass(cls):
        """Выполняет очистку после всего набора тестов."""
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    @staticmethod
    def clear_media_folder():
        """Очищает подпапку posts во временной папке для медиафайлов."""
        shutil.rmtree(os.path.join(TEMP_MEDIA_ROOT, 'posts'),
                      ignore_errors=True)

    def _test_files_are_equal(self, f1, f2):
        """Файлы f1, f2 имеют одинаковое содержимое?"""
        self.assertEqual(f1.size, f2.size)
        f1.open('rb')
        f2.open('rb')
        content1 = f1.read()
        content2 = f2.read()
        f1.close()
        f2.close()
        self.assertEqual(content1, content2)


class BaseTestCaseForPageWithPaginator(BaseTestCaseWithUploadedFiles):
    """Заготовка набора тестов для проверки страниц с паджинатором
    в приложении posts.
    """

    NUMBER_OF_POSTS_ON_FIRST_PAGE = 0
    NUMBER_OF_POSTS_ON_LAST_PAGE = 1

    @classmethod
    def get_post_fields(cls, post_id):
        """Вычисляет и возвращает поля поста в зависимости от его id."""
        return {
            'author': cls.author,
            'group': cls.group,
            'text': f'Запись №{post_id}.',
            'image': cls.create_uploaded_gif(f'simple-{post_id}.gif'),
        }

    @classmethod
    def setUpClass(cls):
        """Создаёт фикстуры для всего набора тестов."""
        super().setUpClass()
        cls.TOTAL_NUMBER_OF_POSTS = (cls.NUMBER_OF_POSTS_ON_FIRST_PAGE
                                     + cls.NUMBER_OF_POSTS_ON_LAST_PAGE)
        cls.url = NotImplemented
        cls.author = User.objects.create_user(username='test-author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-group',
            description='Тестовая группа записей',
        )
        Post.objects.bulk_create(
            Post(id=n + 1, **cls.get_post_fields(n + 1))
            for n in range(cls.TOTAL_NUMBER_OF_POSTS)
        )

    def test_paginator_works_properly(self):
        """Паджинатор на странице работает правильно?"""
        posts_counts_of_pages = {
            1: self.NUMBER_OF_POSTS_ON_FIRST_PAGE,
            2: self.NUMBER_OF_POSTS_ON_LAST_PAGE,
        }
        for page in posts_counts_of_pages:
            with self.subTest(page=page):
                response = self.client.get(self.url, {'page': page})
                expected_posts_count = posts_counts_of_pages[page]
                actual_posts_count = len(response.context['page_obj'])
                self.assertEqual(expected_posts_count, actual_posts_count)

    def test_page_obj_of_context_is_correct(self):
        """В контекст шаблона передано верное значение page_obj?"""
        posts_counts_of_pages = {
            1: self.NUMBER_OF_POSTS_ON_FIRST_PAGE,
            2: self.NUMBER_OF_POSTS_ON_LAST_PAGE,
        }
        for page in posts_counts_of_pages:
            with self.subTest(page=page):
                response = self.client.get(self.url, {'page': page})
                for post in response.context['page_obj']:
                    with self.subTest(post_id=post.pk):
                        exp_post_fields = self.get_post_fields(post.pk)
                        self.assertEqual(post.group,
                                         exp_post_fields['group'])
                        self.assertEqual(post.author,
                                         exp_post_fields['author'])
                        self.assertEqual(post.text,
                                         exp_post_fields['text'])
                        self.assertEqual(
                            post.image.name,
                            'posts/' + exp_post_fields['image'].name
                        )
                        self._test_files_are_equal(
                            post.image,
                            exp_post_fields['image']
                        )


class BaseTestCaseForPostFormView(BaseTestCase):
    """Заготовка набора тестов, проверяющих отображение формы PostForm
    на страницах приложения posts.
    """
    @classmethod
    def setUpClass(cls):
        """Создаёт фикстуры для всего набора тестов."""
        super().setUpClass()
        cls.author = User.objects.create_user(username='test-author')
        cls.url = NotImplemented

    def setUp(self):
        """Создаёт фикстуры для отдельного теста."""
        super().setUp()
        self.client.force_login(self.author)

    def test_page_contains_form_with_proper_fields(self):
        """Страница содержит форму с надлежащими полями?"""
        response = self.client.get(self.url)
        form_fields = {
            'text': forms.CharField,
            'group': forms.ModelChoiceField,
            'image': forms.ImageField,
        }

        for field_name, expected_type in form_fields.items():
            with self.subTest(field=field_name):
                form_field = response.context['form'].fields[field_name]
                self.assertIsInstance(form_field, expected_type)


class BaseTestCaseForPostFormWork(BaseTestCaseWithUploadedFiles):
    """Базовый класс для набора тестов, проверяющих работу формы PostForm."""

    def create_new_post_with_form_and_get_it(self, form_data, client):
        """Создаёт новую запись с помощью формы и возвращает её."""
        # old_post_ids = (post.pk for post in Post.objects.all())
        old_post_ids = list(Post.objects.values_list('pk', flat=True))
        response = client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response, reverse('posts:profile', args=[self.author.username])
        )
        new_posts = Post.objects.exclude(pk__in=old_post_ids)
        self.assertEqual(new_posts.count(), 1)
        return new_posts[0]

    def change_post_with_form_and_get_it(self, post_id, form_data, client):
        """Изменяет запись с помощью формы и возвращает её."""
        old_posts_count = Post.objects.count()
        response = client.post(
            reverse('posts:post_edit', args=[post_id]),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response, reverse('posts:post_detail', args=[post_id])
        )
        self.assertEqual(old_posts_count, Post.objects.count())
        return Post.objects.get(pk=post_id)

    def _test_post_data_corresponds_to_data_given(
        self, post, *, author, text, group, image
    ):
        """Значения полей записи соответствуют требуемым?"""
        self.assertEqual(post.author, author)
        self.assertEqual(post.text, text)
        self.assertEqual(post.group.pk, group)
        self.assertEqual(post.image.name, Post.IMAGES_UPLOAD_PATH + image.name)
        self._test_files_are_equal(post.image, image)


class BaseTestCaseForCommentFormWork(BaseTestCase):
    """Базовый класс для набора тестов, проверяющих работу формы CommentForm.
    """

    def create_new_comment_with_form_and_get_it(
        self, post_id, form_data, client
    ):
        """Создаёт новый комментарий к записи с помощью формы и возвращает его.
        """
        # old_comment_ids = (comment.pk for comment in Comment.objects.all())
        old_comment_ids = list(Comment.objects.values_list('pk', flat=True))
        response = client.post(
            reverse('posts:add_comment', args=[post_id]),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response, reverse('posts:post_detail', args=[post_id])
        )
        new_comments = Comment.objects.exclude(pk__in=old_comment_ids)
        self.assertEqual(new_comments.count(), 1)
        return new_comments[0]

    def _test_comment_data_corresponds_to_data_given(
        self, comment, *, author, text, post
    ):
        """Значения полей комментария к записи соответствуют требуемым?"""
        self.assertEqual(comment.author, author)
        self.assertEqual(comment.text, text)
        self.assertEqual(comment.post, post)
