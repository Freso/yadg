#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url, include
from rest_framework import routers
from .views import TemplateViewSet, ScraperViewSet, ResultView, ApiRootView, MakeQueryView

# Routers provide an easy way of automatically determining the URL conf.
router = routers.SimpleRouter()
router.register(r'templates', TemplateViewSet, base_name='api_v2_template')
router.register(r'scrapers', ScraperViewSet, base_name='api_v2_scraper')

urlpatterns = patterns('',
    url(r'^$', ApiRootView.as_view(), name='api_v2_root'),
    url(r'^', include(router.urls)),
    url(r'^result/(?P<task_id>[^/]+)/$', ResultView.as_view(), name='api_v2_result-detail'),
    url(r'^query/$', MakeQueryView.as_view(), name='api_v2_make-query')
)