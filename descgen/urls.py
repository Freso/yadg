from django.conf.urls.defaults import patterns, url, include

from django.views.generic.base import RedirectView
from django.core.urlresolvers import reverse
from django.utils.functional import lazy

from descgen.views import IndexView,ResultView,DownloadResultView,SettingsView

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

reverse_lazy = lazy(reverse, str)

urlpatterns = patterns('',
    url(r'^$', IndexView.as_view(), name='index'),
    url(r'^result/(?P<id>[\w\d-]+)$', ResultView.as_view(), name='get_result'),
    url(r'^result/(?P<id>[\w\d-]+)/download/(?P<format>[\w\d-]+)$', DownloadResultView.as_view(), name='download_result'),
    url(r'^settings$', SettingsView.as_view(), name='settings'),
    url(r'^api/$', RedirectView.as_view(url=reverse_lazy('api_v1_root'), permanent=False), name='api_root'),
    url(r'^api/v1/', include('descgen.api.v1_urls')),
    # url(r'^whatdesc/', include('whatdesc.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
