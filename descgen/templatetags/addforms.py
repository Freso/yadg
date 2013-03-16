from django import template
from descgen.forms import InputForm, FormatForm
from descgen.formatter import FORMAT_DEFAULT, Formatter
from descgen.scraper.factory import SCRAPER_DEFAULT, ScraperFactory
import re

register = template.Library()

#todo: use @register.assignment_tag for this when updating to Django 1.4
def parse_tag(token):
    # This version uses a regular expression to parse tag contents.
    try:
        # Splitting by None == splitting by spaces.
        tag_name, arg = token.contents.split(None, 1)
    except ValueError:
        raise template.TemplateSyntaxError("%r tag requires arguments" % token.contents.split()[0])
    m = re.search(r'as (\w+)', arg)
    if not m:
        raise template.TemplateSyntaxError("%r tag had invalid arguments" % tag_name)
    var_name = m.group(1)
    return var_name


class InputFormNode(template.Node):
    def __init__(self, var_name):
        self.var_name = var_name

    def render(self, context):
        context[self.var_name] = InputForm(initial={'scraper': ScraperFactory.get_valid_scraper(
            context['request'].session.get("default_scraper", SCRAPER_DEFAULT))})
        return ''


class FormatFormNode(template.Node):
    def __init__(self, var_name):
        self.var_name = var_name

    def render(self, context):
        context[self.var_name] = FormatForm(initial={'description_format': Formatter.get_valid_format(
            context['request'].session.get("default_format", FORMAT_DEFAULT))})
        return ''


@register.tag(name='add_input_form')
def do_input_form(parser, token):
    var_name = parse_tag(token)
    return InputFormNode(var_name)


@register.tag(name='add_format_form')
def do_input_form(parser, token):
    var_name = parse_tag(token)
    return FormatFormNode(var_name)