from django import template

register = template.Library()

def template_visible_to_user(template_obj, user):
    return template_obj.visible_to_user(user, assume_subscription=True)

@register.filter
def getvisiblefor(templates, user):
    return filter(lambda x: template_visible_to_user(x, user), templates)

@register.filter()
def isvisiblefor(template, user):
    return template_visible_to_user(template, user)