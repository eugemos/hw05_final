from django.views.generic.base import TemplateView


class AboutAuthorView(TemplateView):
    """Обеспечивает отображение страницы 'Об авторе'."""

    template_name = 'about/author.html'


class AboutTechView(TemplateView):
    """Обеспечивает отображение страницы 'Технологии'."""

    template_name = 'about/tech.html'
