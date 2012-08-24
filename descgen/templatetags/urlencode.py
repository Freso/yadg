from django import template
from django.utils.http import urlencode

register = template.Library()

@register.filter
def real_urlencode(value):
    return urlencode(value)