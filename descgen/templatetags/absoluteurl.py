from django import template
from django.core.urlresolvers import reverse

register = template.Library()

@register.simple_tag
def absolute_url(request, location):
    url = reverse(location)
    return request.build_absolute_uri(url)