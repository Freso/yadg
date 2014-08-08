from django.conf.urls import patterns, url, include

from django.views.generic.base import RedirectView
from django.core.urlresolvers import reverse_lazy

from .views.misc import IndexView, ResultView, ScrapersView, SettingsView
from .views.scratchpad import ScratchpadIndexView, ScratchpadView, TemplateFromScratchpadView
from .views.template import TemplateAddView, TemplateEditView, TemplateDeleteView, TemplateListView
from .views.user import SubscribeView, SubscriptionsView, UnsubscribeView, UserDetailView, UserListView

urlpatterns = patterns('',
    url(r'^$', IndexView.as_view(), name='index'),
    url(r'^users/$', UserListView.as_view(), name='user_list'),
    url(r'^users/(?P<id>[\d]+)$', UserDetailView.as_view(), name='user_detail'),
    url(r'^subscribe$', SubscribeView.as_view(), name='subscribe_to_user'),
    url(r'^unsubscribe$', UnsubscribeView.as_view(), name='unsubscribe'),
    url(r'^subscriptions/$', SubscriptionsView.as_view(), name='subscriptions'),
    url(r'^templates/$', TemplateListView.as_view(), name='template_list'),
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
)
