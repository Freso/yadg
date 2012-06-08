from django import template

register = template.Library()

@register.filter
def sorteditems(value):
    items = []
    if value is not None:
        #sort keys
        keys = value.keys()
        keys.sort()
        #build (key,value) list
        for key in keys:
            items.append((key,value[key]))
    return items