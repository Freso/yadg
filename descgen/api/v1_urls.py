from django.conf.urls.defaults import patterns, url
from v1 import ScraperList,FormatList,Root,MakeQuery,Result

urlpatterns = patterns('',
    url(r'^$', Root.as_view(), name="api_v1_root"),                   
    url(r'^query/$', MakeQuery.as_view(), name="api_v1_makequery"),
    url(r'^scrapers/$', ScraperList.as_view(), name="api_v1_scraperlist"),
    url(r'^formats/$', FormatList.as_view(), name="api_v1_formatlist"),
    url(r'^result/(?P<id>[\w\d-]+)/$', Result.as_view(), name="api_v1_result"),
)