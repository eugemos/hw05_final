"""Тесты для проверки URL приложения posts."""
from django.test import Client
from django.urls import reverse

from core.tests.utils import BaseRuledURLTestCase
from users.models import User
from posts.models import Post, Group


class URLTestCase(BaseRuledURLTestCase):
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

    def test_urls(self):
        """Проверяет URL приложения post в соответствии с правилами."""
        authorized_client = Client()
        authorized_client.force_login(self.user)
        author_client = Client()
        author_client.force_login(self.author)
        nonexistent_post_id = self.post.pk + 1

        rules = {
            '/': (
                self.must_be_accessible(self.client, 'posts/index.html'),
            ),
            f'/group/{self.group.slug}/': (
                self.must_be_accessible(self.client, 'posts/group_list.html'),
            ),
            f'/profile/{self.author.username}/': (
                self.must_be_accessible(self.client, 'posts/profile.html'),
            ),
            f'/posts/{self.post.pk}/': (
                self.must_be_accessible(self.client, 'posts/post_detail.html'),
            ),

            '/create/': (
                self.must_be_accessible(authorized_client,
                                        'posts/create_post.html'),
                self.must_redirect_to_login(self.client),
            ),
            '/follow/': (
                self.must_be_accessible(authorized_client,
                                        'posts/follow.html'),
                self.must_redirect_to_login(self.client),
            ),

            f'/posts/{self.post.pk}/comment/': (
                self.must_redirect(
                    authorized_client,
                    reverse('posts:post_detail', args=[self.post.pk])
                ),
                self.must_redirect_to_login(self.client),
            ),
            f'/profile/{self.author.username}/follow/': (
                self.must_redirect(
                    authorized_client,
                    reverse('posts:profile', args=[self.author.username])
                ),
                self.must_redirect_to_login(self.client),
            ),
            f'/profile/{self.author.username}/unfollow/': (
                self.must_redirect(
                    authorized_client,
                    reverse('posts:profile', args=[self.author.username])
                ),
                self.must_redirect_to_login(self.client),
            ),

            f'/posts/{self.post.pk}/edit/': (
                self.must_be_accessible(author_client,
                                        'posts/create_post.html'),
                self.must_redirect(
                    authorized_client,
                    reverse('posts:post_detail', args=[self.post.pk])
                ),
                self.must_redirect_to_login(self.client),
            ),

            '/nonexistent_page/': (self.must_be_inaccessible(author_client),),
            '/group/nonexistent_slug/':
                (self.must_be_inaccessible(author_client),),
            '/profile/nonexistent_username/':
                (self.must_be_inaccessible(author_client),),
            '/profile/nonexistent_username/follow/':
                (self.must_be_inaccessible(author_client),),
            '/profile/nonexistent_username/unfollow/':
                (self.must_be_inaccessible(author_client),),
            f'/posts/{nonexistent_post_id}/':
                (self.must_be_inaccessible(author_client),),
            f'/posts/{nonexistent_post_id}/edit/':
                (self.must_be_inaccessible(author_client),),
            f'/posts/{nonexistent_post_id}/comment/':
                (self.must_be_inaccessible(author_client),),
        }

        self.execute(rules)
