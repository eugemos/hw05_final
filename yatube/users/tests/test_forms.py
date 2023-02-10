"""Тесты для проверки форм в приложении users."""
from django.test import TestCase
from django.urls import reverse

from users.models import User


class UserCreationFormTestCase(TestCase):
    """Набор тестов для проверки формы создания нового пользователя."""

    def test_valid_form_on_signup_page_creates_new_user(self):
        """Валидная форма на странице signup создаёт нового пользователя?"""
        users_count = User.objects.count()
        form_data = {
            'first_name': 'Тест',
            'last_name': 'Тестов',
            'username': 'test',
            'email': 'test@test.tst',
            'password1': 'Yandex-2023-Practicum',
            'password2': 'Yandex-2023-Practicum',
        }
        response = self.client.post(
            reverse('users:signup'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response, reverse('posts:index')
        )
        self.assertEqual(User.objects.count(), users_count + 1)
        self.assertTrue(
            User.objects.filter(
                username=form_data['username'],
            ).exists()
        )
