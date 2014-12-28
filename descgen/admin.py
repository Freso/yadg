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

from django.contrib import admin
from .models import Template, Subscription, DependencyClosure, Settings
from .forms import TemplateAdminForm, SettingsAdminForm


class TemplateAdmin(admin.ModelAdmin):
    form = TemplateAdminForm
    list_display = ('name', 'owner', 'is_public', 'is_default', 'is_utility', 'depends_on', 'dependencies_set', 'cached_dependencies_set')


class SettingsAdmin(admin.ModelAdmin):
    form = SettingsAdminForm

admin.site.register(Template, TemplateAdmin)
admin.site.register(Subscription)
admin.site.register(DependencyClosure)
admin.site.register(Settings, SettingsAdmin)