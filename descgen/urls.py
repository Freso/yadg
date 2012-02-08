from django.conf.urls.defaults import patterns, url, include

from django.views.generic.base import RedirectView
from django.core.urlresolvers import reverse
from django.utils.functional import lazy

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

reverse_lazy = lazy(reverse, str)

urlpatterns = patterns('descgen.views',
    url(r'^$', 'index', name='index'),
    url(r'^get/(?P<scraper>\w+)/(?P<id>[^\/]+)$', 'get_by_id', name='get_by_id'),
    url(r'^result/(?P<id>[\w\d-]+)$', 'get_result', name='get_result'),
    url(r'^result/(?P<id>[\w\d-]+)/download/(?P<format>[\w\d-]+)$', 'download_result', name='download_result'),
    url(r'^api/$', RedirectView.as_view(url=reverse_lazy('api_v1_root')), name='api_root'),
    url(r'^api/v1/', include('descgen.api.v1_urls')),
    # url(r'^whatdesc/', include('whatdesc.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
