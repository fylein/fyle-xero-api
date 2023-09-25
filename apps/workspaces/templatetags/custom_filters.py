from django import template

register = template.Library()


@register.filter
def snake_case_to_space_case(value):
    return " ".join(word.capitalize() for word in value.split("_"))
