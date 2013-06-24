from django import template

register = template.Library()

@register.filter
def formatseconds(value):
    return '%02d:%02d' % divmod(value, 60)