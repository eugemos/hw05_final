"""Функции отображения кастомных страниц для ошибок."""
from http import HTTPStatus

from django.shortcuts import render


def page_not_found(request, exception):
    """Отображает кастомную страницу для ошибки 404."""
    context = {'path': request.path}
    return render(
        request, 'core/404.html', context, status=HTTPStatus.NOT_FOUND
    )


def csrf_failure(request, reason=''):
    """Отображает кастомную страницу для ошибки 403."""
    return render(request, 'core/403csrf.html')
