from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^contact/', include('contact.urls')),
    url(r'^login$', 'descgen.views.login', {'template_name': 'login.html'}, name='login'),
    url(r'^logout$', 'descgen.views.logout', {'template_name': 'logged_out.html'}, name='logout'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include('descgen.urls'))
)
