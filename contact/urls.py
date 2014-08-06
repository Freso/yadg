#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
from .views import ContactView, ContactSuccessView, ContactErrorView

urlpatterns = patterns('',
    url(r'^$', ContactView.as_view(), name='contact'),
    url(r'^success$', ContactSuccessView.as_view(), name='contact_success'),
    url(r'^error', ContactErrorView.as_view(), name='contact_error'),
)