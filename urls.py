from django.conf.urls import patterns, include, url
from django.core.urlresolvers import reverse_lazy

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^contact/', include('contact.urls')),
    url(r'^login$', 'descgen.views.login', {'template_name': 'login.html'}, name='login'),
    url(r'^logout$', 'descgen.views.logout', {'template_name': 'logged_out.html'}, name='logout'),
    url(r'^password$', 'django.contrib.auth.views.password_change', {'template_name': 'password_change.html', 'post_change_redirect': reverse_lazy('password_change_done')}, name='password_change'),
    url(r'^password/done$', 'django.contrib.auth.views.password_change_done', {'template_name': 'password_change_done.html'}, name='password_change_done'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include('descgen.urls'))
)
