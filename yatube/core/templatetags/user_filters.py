from django import template

register = template.Library()


@register.filter
def addclass(field, css):
    """Добавляет класс css к полю формы."""
    return field.as_widget(attrs={'class': css})
