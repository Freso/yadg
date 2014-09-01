import requests
import re
import logging


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
        self.initialize_new_session()

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

    def initialize_new_session(self):
        self.session = requests.Session()

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


class Scraper(object):

    string_regex = None

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


class Factory(object):

    def get_scraper_by_string(self, string):
        return None

    def get_search_scraper(self, search_term):
        return None

    def has_search(self):
        return False


class StandardFactory(Factory):

    scraper_classes = []
    search_scraper = None

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

    def is_searchable(self):
        return self.has_search()



