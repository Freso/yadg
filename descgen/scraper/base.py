import requests


class APIBase(object):
    
    _base_url = None
    _exception = None
    _object_id = ''
    
    def __init__(self):
        self._cached_response = None
        self._url_appendix = None
        self._params = None
        self._headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:6.0.2) Gecko/20100101 Firefox/6.0.2'}
    
    @property
    def _response(self):
        if not self._cached_response:
            r = requests.get(self._base_url + self._url_appendix, params=self._params, headers=self._headers)
            if r.status_code == 200:
                self._cached_response = r
            else:
                raise self._exception, '%d' % r.status_code
        return self._cached_response
    
    def _remove_whitespace(self, string):
        return ' '.join(string.split())
    
    def _raise_exception(self,message):
        raise self._exception, u'%s [%s]' % (message,self._object_id)