from django import template
from ..models import Subscription

register = template.Library()

@register.filter
def subscribedto(user1, user2):
    return Subscription.objects.filter(subscriber_id__exact=user1.pk, user_id__exact=user2.pk).exists()