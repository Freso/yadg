from django.conf.urls.defaults import patterns, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('descgen.views',
    url(r'^$', 'index', name='index'),
    url(r'^get/(?P<id>\d+)$', 'get_by_discogs_id', name='get_by_discogs_id'),
    url(r'^result/(?P<id>[\w\d-]+)$', 'get_result', name='get_result'),
    # url(r'^whatdesc/', include('whatdesc.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
