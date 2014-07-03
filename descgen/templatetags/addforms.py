from django import template
from descgen.forms import InputForm, FormatForm, SubscribeForm
from descgen.formatter import FORMAT_DEFAULT, Formatter
from descgen.scraper.factory import SCRAPER_DEFAULT, ScraperFactory

register = template.Library()

@register.assignment_tag(takes_context=True)
def add_input_form(context):
    return InputForm(initial={'scraper': ScraperFactory.get_valid_scraper(
            context['request'].session.get("default_scraper", SCRAPER_DEFAULT))})

@register.assignment_tag(takes_context=True)
def add_format_form(context):
    return FormatForm(initial={'description_format': Formatter.get_valid_format(
            context['request'].session.get("default_format", FORMAT_DEFAULT))})

@register.filter
def subscribe_form(user):
    return SubscribeForm(initial={'user_id': user.pk})