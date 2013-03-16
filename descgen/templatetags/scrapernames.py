from django import template
from descgen.scraper.factory import SCRAPER_CHOICES
import re

register = template.Library()


class ScraperNamesNode(template.Node):
    def __init__(self, var_name):
        self.var_name = var_name

    def render(self, context):
        scraper_names = map(lambda x: x[1], SCRAPER_CHOICES)
        scraper_names.sort()
        context[self.var_name] = scraper_names
        return ''


@register.tag(name='scraper_names')
def do_scraper_names(parser, token):
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
    return ScraperNamesNode(var_name)