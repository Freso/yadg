from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^contact/', include('contact.urls')),
    (r'^admin/', include(admin.site.urls)),
    url(r'^', include('descgen.urls'))
)
