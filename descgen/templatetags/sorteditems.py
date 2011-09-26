from django import template
import re

register = template.Library()

@register.filter
def sorteditems(value):
    items = []
    #sort keys
    keys = value.keys()
    keys.sort()
    #build (key,value) list
    for key in keys:
        items.append((key,value[key]))
    return items