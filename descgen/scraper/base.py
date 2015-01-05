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

import requests
import re
import logging
import datetime
import time
from collections import defaultdict


class ScraperError(Exception):
    pass


class ExceptionMixin(object):

    exception = ScraperError

    def get_exception(self):
        return self.exception

    def raise_exception(self, message):
        raise self.get_exception(), u'%s [%s]' % (message, unicode(self))


class StatusCodeError(requests.RequestException):
    """The request returned a status code that was not 200"""
    pass


class RequestMixin(object):

    REQUEST_METHOD_POST = "post"
    REQUEST_METHOD_GET = "get"

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:21.0) Gecko/20100101 Firefox/21.0'}
    request_kwargs = {}
    forced_response_encoding = None

    def __init__(self):
        super(RequestMixin, self).__init__()
        self.session = self.get_new_session()

    def _make_request(self, method, url, params, headers, post_data, kwargs):
        """
        The internal method that makes the actual request and returns a response object. This should normally not be used
        directly.
        """
        if headers is None:
            headers = self.get_headers()
        if kwargs is None:
            kwargs = self.get_request_kwargs()
        if method == self.REQUEST_METHOD_POST:
            r = self.session.post(url=url, data=post_data, params=params, headers=headers, **kwargs)
        else:
            r = self.session.get(url=url, params=params, headers=headers, **kwargs)
        if r.status_code != 200:
            self.raise_request_exception(r.status_code if r.status_code else 500)
        forced_encoding = self.get_forced_response_encoding()
        if forced_encoding:
            r.encoding = forced_encoding
        return r

    def request_get(self, url, params=None, headers=None, kwargs=None):
        return self._make_request(method=self.REQUEST_METHOD_GET, url=url, params=params, headers=headers, post_data=None, kwargs=kwargs)

    def request_post(self, url, post_data=None, params=None, headers=None, kwargs=None):
        return self._make_request(method=self.REQUEST_METHOD_GET, url=url, params=params, headers=headers, post_data=post_data, kwargs=kwargs)

    def get_new_session(self):
        return requests.Session()

    def raise_request_exception(self, message):
        raise StatusCodeError(message)

    def get_headers(self):
        return self.headers

    def get_request_kwargs(self):
        return self.request_kwargs

    def get_forced_response_encoding(self):
        return self.forced_response_encoding

    def get_response_content(self, response):
        return response.text


class UtilityMixin(object):

    presuffixes = [
        (u'The ', u', The'),
        (u'A ', u', A'),
    ]

    def get_presuffixes(self):
        return self.presuffixes

    def swap_suffix(self, string):
        for (prefix, suffix) in self.get_presuffixes():
            if string.endswith(suffix):
                string = prefix + string[:-len(suffix)]
                #we assume there is only one suffix to swap
                break
        return string

    def remove_whitespace(self, string):
        return ' '.join(string.split())

    def seconds_from_string(self, length_string):
        i = 0
        length = 0
        for component in reversed(length_string.split(':')):
            try:
                length += int(component) * 60 ** i
            except ValueError:
                return None
            i += 1
        return length


class LoggerMixin(object):

    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL

    _logger = None

    def get_logger(self):
        if self._logger is None:
            self._logger = logging.getLogger(name=self.__module__ + '.' + self.__class__.__name__)
        return self._logger

    def get_extra_log_kwargs(self):
        return {'instance': unicode(self)}

    def log(self, level, msg):
        logger = self.get_logger()
        logger.log(level, msg, extra=self.get_extra_log_kwargs())

    def log_debug(self, msg):
        self.log(self.DEBUG, msg)

    def log_info(self, msg):
        self.log(self.INFO, msg)

    def log_warning(self, msg):
        self.log(self.WARNING, msg)

    def log_error(self, msg):
        self.log(self.ERROR, msg)

    def log_critical(self, msg):
        self.log(self.CRITICAL, msg)


class RateLimitMixin(object):

    _last_call_time = None
    _rate_limit_interval = None

    def get_rate_limit_value(self):
        return self.rate_limit

    def raise_rate_limit_format_error(self, rate_limit_format):
        raise ValueError(u'invalid rate limit format: %s' % rate_limit_format)

    def calculate_rate_limit_interval(self):
        rate_limit = self.get_rate_limit_value()
        components = rate_limit.split('/')
        if len(components) == 1:
            # interpret value as seconds
            number_of_calls_string = components[0]
            base = 1.0
        elif len(components) == 2:
            number_of_calls_string = components[0]
            base_string = components[1]
            if base_string == 's':
                base = 1.0
            elif base_string == 'm':
                base = 60.0
            elif base_string == 'h':
                base = 60.0 * 60.0
            else:
                self.raise_rate_limit_format_error(rate_limit)
        else:
            self.raise_rate_limit_format_error(rate_limit)
        try:
            number_of_calls = float(components[0])
        except ValueError:
            self.raise_rate_limit_format_error(rate_limit)
        self._rate_limit_interval = datetime.timedelta(seconds=base/number_of_calls)

    def get_rate_limit_interval(self):
        if self._rate_limit_interval is None:
            self.calculate_rate_limit_interval()
        return self._rate_limit_interval

    def rate_limit_sleep(self):
        if self._last_call_time is not None:
            last_call_delta = datetime.datetime.now() - self._last_call_time
            rate_limit_interval = self.get_rate_limit_interval()
            if last_call_delta < rate_limit_interval:
                delta = rate_limit_interval - last_call_delta
                delta_seconds = (delta.microseconds + (delta.seconds + delta.days * 24 * 3600) * 10**6) / 10.0**6
                time.sleep(delta_seconds)
        self._last_call_time = datetime.datetime.now()


class Scraper(object):

    string_regex = None
    rate_limit = None

    def __init__(self):
        super(Scraper, self).__init__()
        self.name = None
        self.original_string = None

    def get_result(self):
        raise NotImplementedError()

    def set_name(self, name):
        self.name = name

    def get_name(self):
        return self.name

    def set_original_string(self, original_url):
        self.original_string = original_url

    def get_original_string(self):
        return self.original_string

    def get_instance_info(self):
        return u""

    @staticmethod
    def _get_args_from_match(match):
        return match.groups()

    @classmethod
    def from_string(cls, string):
        if cls.string_regex is not None:
            m = re.match(cls.string_regex, string)
            if m:
                scraper = cls(*cls._get_args_from_match(m))
                scraper.set_original_string(string)
                return scraper
        return None

    def __unicode__(self):
        return u"<%s: %s>" % (self.__class__.__name__, self.get_instance_info())


class SearchScraper(Scraper):

    def __init__(self, search_term):
        super(SearchScraper, self).__init__()
        self.search_term = search_term

    def get_instance_info(self):
        return u'search_term="%s"' % self.search_term


class RateLimitGroup(object):

    def __init__(self, rate_limit=None, objects=[]):
        super(RateLimitGroup, self).__init__()
        self.rate_limit = rate_limit
        self.objects = objects

    def set_rate_limit(self, rate_limit):
        self.rate_limit = rate_limit

    def get_rate_limit(self):
        return self.rate_limit

    def append_object(self, object):
        self.objects.append(object)

    def get_objects(self):
        return self.objects


class Factory(object):

    RateLimitGroup = RateLimitGroup

    def __init__(self):
        super(Factory, self).__init__()
        self.rate_limit_groups = []

    def get_scraper_by_string(self, string):
        return None

    def get_search_scraper(self, search_term):
        return None

    def has_search(self):
        return False

    def is_searchable(self):
        return self.has_search()

    def create_rate_limit_group(self, *args, **kwargs):
        return self.RateLimitGroup(*args, **kwargs)

    def append_rate_limit_group(self, rate_limit_group):
        self.rate_limit_groups.append(rate_limit_group)

    def get_rate_limit_groups(self):
        return self.rate_limit_groups


class StandardFactory(Factory):

    scraper_classes = []
    search_scraper = None

    '''
    Force a specific grouping of scrapers into rate limit groups by providing a list in the following format:
    [
        ('100/s', [
            ScraperClass1,
            ScraperClass2,
            ...
        ]),
        ('100/m', [
            ScraperClass3,
            ScraperClass4,
            ...
        ]),
        ...
    ]
    '''
    force_rate_limit_groups = []

    '''
    Set a rate limit for all classes known to this factory. All known scraper classes will be part of the same rate
    limit group with this rate limit.

    If force_rate_limit_groups is also provided, force_rate_limit_groups will take precedence.
    '''
    global_rate_limit = None

    def __init__(self):
        super(StandardFactory, self).__init__()
        self.create_rate_limit_groups()

    def get_search_scraper(self, search_term):
        if self.search_scraper is not None:
            return self.search_scraper(search_term=search_term)
        return None

    def get_scraper_by_string(self, string):
        for scraper_class in self.scraper_classes:
            scraper = scraper_class.from_string(string)
            if scraper is not None:
                return scraper
        return None

    def has_search(self):
        return self.search_scraper is not None

    def create_rate_limit_groups(self):
        if not self.force_rate_limit_groups:
            scraper_classes = list(self.scraper_classes)
            if self.search_scraper:
                scraper_classes.append(self.search_scraper)
            rate_limit_bins = defaultdict(list)
            # if a global rate limit is set, we set this rate limit for all classes known to this factory
            if self.global_rate_limit is not None:
                rate_limit_bins[self.global_rate_limit].extend(scraper_classes)
            else:
                # otherwise we look at scraper specific rate limits
                for scraper_class in scraper_classes:
                    rate_limit = getattr(scraper_class, 'rate_limit', None)
                    if rate_limit:
                        rate_limit_bins[rate_limit].append(scraper_class)
            items = rate_limit_bins.items()
        else:
            items = self.force_rate_limit_groups
        # make sure the order of the rate_limit_groups is consistent over multiple executions
        for rate_limit, objects in sorted(items, key=lambda(k, v): (k, str(v))):
            rate_limit_group = self.create_rate_limit_group(rate_limit, objects)
            self.append_rate_limit_group(rate_limit_group)