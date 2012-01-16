from django.conf.urls.defaults import patterns, url
from v1 import SearchQuery,IdQuery,ScraperList,FormatList

urlpatterns = patterns('',
    url(r'^query\.phrase$', SearchQuery.as_view(), name="api_v1_searchquery"),
    url(r'^query\.id$', IdQuery.as_view(), name="api_v1_idquery"),
    url(r'^scrapers$', ScraperList.as_view(), name="api_v1_scraperlist"),
    url(r'^formats$', FormatList.as_view(), name="api_v1_formatlist"),
)