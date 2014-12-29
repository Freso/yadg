#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2011-2015 Slack
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

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