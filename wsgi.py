import os
import sys
import site

site.addsitedir('/home/yadg/djangoenv/lib/python2.6/site-packages')

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()