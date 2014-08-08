from django import template
from descgen.forms import InputForm, FormatForm, SubscribeForm
from ..mixins import CreateTaskMixin


class ScraperGetter(CreateTaskMixin):

    def __init__(self, request):
        self.request = request


register = template.Library()

@register.assignment_tag(takes_context=True)
def add_input_form(context):
    sg = ScraperGetter(context['request'])
    return InputForm(initial={'scraper': sg.get_valid_scraper(None)})

@register.filter
def subscribe_form(user):
    return SubscribeForm(initial={'user_id': user.pk})