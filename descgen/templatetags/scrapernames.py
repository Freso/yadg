from django import template
from descgen.scraper.factory import SCRAPER_ITEMS

register = template.Library()

@register.assignment_tag()
def scraper_names():
    return map(lambda x: x['name'], filter(lambda x: x['release'], SCRAPER_ITEMS))