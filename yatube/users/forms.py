from django.contrib.auth.forms import UserCreationForm

from .models import User


class CreationForm(UserCreationForm):
    """Представляет форму для регистрации пользователя на сайте."""

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')
