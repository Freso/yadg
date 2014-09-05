from django.conf.urls import patterns, url, include

from django.views.generic.base import RedirectView
from django.core.urlresolvers import reverse_lazy

from .views.misc import IndexView, ResultView, ScrapersView, SettingsView, ApiTokenView
from .views.scratchpad import ScratchpadIndexView, ScratchpadView, TemplateFromScratchpadView
from .views.template import TemplateAddView, TemplateEditView, TemplateDeleteView, TemplateListView, TemplateCopyView
from .views.user import SubscribeView, SubscriptionsView, UnsubscribeView, UserDetailView, UserListView
from .views.auth import RegisterView


urlpatterns = patterns('',
    url(r'^$', IndexView.as_view(), name='index'),

    url(r'^register$', RegisterView.as_view(), name='register'),
    url(r'^login$', 'descgen.views.auth.login', {'template_name': 'auth/login.html'}, name='login'),
    url(r'^logout$', 'descgen.views.auth.logout', {'template_name': 'auth/logged_out.html'}, name='logout'),
    url(r'^password$', 'django.contrib.auth.views.password_change', {'template_name': 'auth/password_change.html', 'post_change_redirect': reverse_lazy('password_change_done')}, name='password_change'),
    url(r'^password/done$', 'django.contrib.auth.views.password_change_done', {'template_name': 'auth/password_change_done.html'}, name='password_change_done'),

    url(r'^users/$', UserListView.as_view(), name='user_list'),
    url(r'^users/(?P<id>[\d]+)$', UserDetailView.as_view(), name='user_detail'),
    url(r'^subscribe$', SubscribeView.as_view(), name='subscribe_to_user'),
    url(r'^unsubscribe$', UnsubscribeView.as_view(), name='unsubscribe'),
    url(r'^subscriptions/$', SubscriptionsView.as_view(), name='subscriptions'),

    url(r'^templates/$', TemplateListView.as_view(), name='template_list'),
    url(r'^templates/add$', TemplateAddView.as_view(), name='template_add'),
    url(r'^templates/copy/(?P<id>[\d]+)$', TemplateCopyView.as_view(), name='template_copy'),
    url(r'^templates/delete$', TemplateDeleteView.as_view(), name='template_delete'),
    url(r'^templates/scratchpad(?:/(?P<id>[\d]+))?$', TemplateFromScratchpadView.as_view(), name='template_from_scratchpad'),
    url(r'^templates/(?P<id>[\d]+)$', TemplateEditView.as_view(), name='template_edit'),

    url(r'^scratchpad$', ScratchpadIndexView.as_view(), name='scratchpad_index'),
    url(r'^scratchpad/(?P<id>[\w\d-]+)$', ScratchpadView.as_view(), name='scratchpad'),

    url(r'^result/(?P<id>[\w\d-]+)$', ResultView.as_view(), name='get_result'),

    url(r'^settings$', SettingsView.as_view(), name='settings'),
    url(r'^available-scrapers$', ScrapersView.as_view(), name='scrapers_overview'),

    url(r'^api/token$', ApiTokenView.as_view(), name='api_token'),
    url(r'^api/$', RedirectView.as_view(url=reverse_lazy('api_v2_root'), permanent=False), name='api_root'),
    url(r'^api/v2/', include('descgen.api.v2.urls'))
)
