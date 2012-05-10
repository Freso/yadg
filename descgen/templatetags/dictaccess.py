from django import template

register = template.Library()

@register.filter
def get(value,arg):
    if value.has_key(arg):
        return value[arg]
    return None