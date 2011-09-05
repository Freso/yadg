from django import template
import re

register = template.Library()

@register.filter
def isdigit(value):
    m = re.search('\D',value)
    if m:
        return False
    else:
        return True