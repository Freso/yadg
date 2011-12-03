from django.conf import settings
from django.http import HttpResponse

#get the config values
XS_SHARING_ALLOWED_ORIGINS = getattr(settings, 'XS_SHARING_ALLOWED_ORIGINS', '*')
XS_SHARING_ALLOWED_METHODS = getattr(settings, 'XS_SHARING_ALLOWED_METHODS', ['POST','GET','OPTIONS', 'PUT', 'DELETE'])

class XsSharing(object):
    """
        This middleware allows cross domain requests for Ajax requests

        Access-Control-Allow-Origin: http://foo.example
        Access-Control-Allow-Methods: POST, GET, OPTIONS, PUT, DELETE
    """
    def process_response(self, request, response):
        # Avoid unnecessary work
        if response.has_header('Access-Control-Allow-Origin'):
            return response
        # Only set the headers if it is an ajax request
        elif request.GET.has_key("xhr"):
            response['Access-Control-Allow-Origin'] = XS_SHARING_ALLOWED_ORIGINS
            response['Access-Control-Allow-Methods'] = ",".join( XS_SHARING_ALLOWED_METHODS )
        
        return response