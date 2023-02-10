from django.core.paginator import Paginator


def make_page_obj(request, content, page_size):
    """Формирует запрошенную страницу контента."""
    paginator = Paginator(content, page_size)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
