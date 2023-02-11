""""""
from http import HTTPStatus

from django.shortcuts import render


def page_not_found(request, exception):
    context =  {'path': request.path}
    return render(
        request, 'core/404.html', context, status=HTTPStatus.NOT_FOUND
    )


def csrf_failure(request, reason=''):
    return render(request, 'core/403csrf.html')
