from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter()
def yesnoimg(val):
    if val:
        out = '<i class="icon-ok" title="Yes"></i><span class="hide">Yes</span>'
    else:
        out = '<i class="icon-remove" title="No"></i><span class="hide">No</span>'
    return mark_safe(out)