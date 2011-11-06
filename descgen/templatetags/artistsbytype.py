from django import template

register = template.Library()

@register.filter
def artistsbytype(value,arg):
    return map(lambda x: x['name'],filter(lambda x: x['type'] == arg,value))