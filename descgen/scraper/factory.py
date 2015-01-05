#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2011-2015 Slack
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import discogs
import musicbrainz
#import beatport
import metalarchives
import junodownload
import itunes
import bandcamp
import musiksammler

_SCRAPERS = {
    'discogs': {'module': discogs, 'priority': 10},
    'musicbrainz': {'module': musicbrainz, 'priority': 10},
    #'beatport': {'module': beatport, 'priority': 10},
    'metalarchives': {'module': metalarchives, 'priority': 10},
    'junodownload': {'module': junodownload, 'priority': 10},
    'itunes': {'module': itunes, 'priority': 10},
    'bandcamp': {'module': bandcamp, 'priority': 15},
    'musiksammler': {'module': musiksammler, 'priority': 10},
}

_SCRAPER_FACTORIES = {}
_SCRAPER_FACTORIES_SORTED = []
SCRAPER_ITEMS = []
SCRAPER_CHOICES = []
SCRAPER = []

for scraper_key in sorted(_SCRAPERS):
    scraper = _SCRAPERS[scraper_key]['module']
    _SCRAPER_FACTORIES[scraper_key] = scraper.ScraperFactory()
    _SCRAPER_FACTORIES_SORTED.append({'factory': _SCRAPER_FACTORIES[scraper_key], 'name': scraper_key})
    has_release = True
    has_search = _SCRAPER_FACTORIES[scraper_key].has_search()
    is_searchable = _SCRAPER_FACTORIES[scraper_key].is_searchable()
    readable_name = scraper.READABLE_NAME
    url = scraper.SCRAPER_URL
    if has_search:
        # the scraper is searchable, so add it to the list of scraper choices used by the forms
        SCRAPER_CHOICES.append((scraper_key, readable_name))
        SCRAPER.append(scraper_key)
    scraper_item = {
        'name': readable_name,
        'url': url,
        'release': has_release,
        'searchable': is_searchable
    }
    if hasattr(scraper, 'NOTES'):
        scraper_item['notes'] = scraper.NOTES
    SCRAPER_ITEMS.append(scraper_item)

_SCRAPER_FACTORIES_SORTED.sort(lambda x, y: cmp(_SCRAPERS[x['name']]['priority'], _SCRAPERS[y['name']]['priority']))

SCRAPER_DEFAULT = 'discogs'


class ScraperFactoryError(Exception):
    pass


class ScraperFactory(object):

    def __init__(self):
        super(ScraperFactory, self).__init__()
        self.rate_limit_groups = None
    
    def get_scraper_by_string(self, url):
        scraper = None
        
        for factory in _SCRAPER_FACTORIES_SORTED:
            scraper = factory['factory'].get_scraper_by_string(url)
            if scraper:
                scraper.set_name(factory['name'])
                break
        
        return scraper
    
    def get_search_scraper(self, search_term, scraper=SCRAPER_DEFAULT):
        if not scraper:
            scraper = SCRAPER_DEFAULT
        if not scraper in SCRAPER:
            raise ScraperFactoryError(u'no searchable scraper "%s"' % scraper)
        
        search = _SCRAPER_FACTORIES[scraper].get_search_scraper(search_term)
        search.set_name(scraper)
        
        return search

    def get_rate_limit_groups(self):
        if self.rate_limit_groups is None:
            self.rate_limit_groups = []
            for factory in _SCRAPER_FACTORIES_SORTED:
                self.rate_limit_groups.extend(factory['factory'].get_rate_limit_groups())
        return self.rate_limit_groups

    @staticmethod
    def get_valid_scraper(scraper):
        if not scraper in SCRAPER:
            scraper = SCRAPER_DEFAULT
        return scraper