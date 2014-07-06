from django.conf.urls import patterns, url, include

from django.views.generic.base import RedirectView
from django.core.urlresolvers import reverse
from django.utils.functional import lazy

from descgen.views import IndexView,ResultView,SettingsView,ScrapersView,ScratchpadView,UserListView,SubscribeView, UnsubscribeView, TemplateEditView, TemplateAddView, TemplateListView, TemplateDeleteView, TemplateFromScratchpadView, ScratchpadIndexView

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

reverse_lazy = lazy(reverse, str)

urlpatterns = patterns('',
    url(r'^$', IndexView.as_view(), name='index'),
    url(r'^users$', UserListView.as_view(), name='user_list'),
    url(r'^subscribe$', SubscribeView.as_view(), name='subscribe_to_user'),
    url(r'^unsubscribe$', UnsubscribeView.as_view(), name='unsubscribe'),
    url(r'^templates$', TemplateListView.as_view(), name='template_list'),
    url(r'^templates/add$', TemplateAddView.as_view(), name='template_add'),
    url(r'^templates/delete$', TemplateDeleteView.as_view(), name='template_delete'),
    url(r'^templates/scratchpad(?:/(?P<id>[\d]+))?$', TemplateFromScratchpadView.as_view(), name='template_from_scratchpad'),
    url(r'^templates/(?P<id>[\d]+)$', TemplateEditView.as_view(), name='template_edit'),
    url(r'^scratchpad$', ScratchpadIndexView.as_view(), name='scratchpad_index'),
    url(r'^scratchpad/(?P<id>[\w\d-]+)$', ScratchpadView.as_view(), name='scratchpad'),
    url(r'^result/(?P<id>[\w\d-]+)$', ResultView.as_view(), name='get_result'),
    url(r'^settings$', SettingsView.as_view(), name='settings'),
    url(r'^available-scrapers$', ScrapersView.as_view(), name='scrapers_overview'),
    url(r'^api/$', RedirectView.as_view(url=reverse_lazy('api_v1_root'), permanent=False), name='api_root'),
    url(r'^api/v1/', include('descgen.api.v1_urls')),
    # url(r'^whatdesc/', include('whatdesc.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
