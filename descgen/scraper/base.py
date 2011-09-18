import requests


class APIBase(object):
    
    _base_url = None
    _exception = None
    _object_id = ''
    
    def __init__(self):
        self._cached_response = None
        self._url_appendix = None
        self._params = None
    
    @property
    def _response(self):
        if not self._cached_response:
            r = requests.get(self._base_url + self._url_appendix, params=self._params)
            if r.status_code == 200:
                self._cached_response = r
            else:
                raise self._exception, '%d' % r.status_code
        return self._cached_response
    
    def _remove_whitespace(self, string):
        return ' '.join(string.split())
    
    def _raise_exception(self,message):
        raise self._exception, u'%s [%s]' % (message,self._object_id)