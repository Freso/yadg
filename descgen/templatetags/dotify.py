from django import template

register = template.Library()

@register.filter
def dotify(value):
    return value.replace(' ','.')