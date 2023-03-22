from django import template

register = template.Library()

@register.filter
def snake_to_space(value):
    return ' '.join(word.capitalize() for word in value.split('_'))
