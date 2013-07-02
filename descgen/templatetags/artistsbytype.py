from django import template

register = template.Library()

@register.filter
def artistsbytype(value, arg):
    return filter(lambda x: arg in x.get_types(), value)