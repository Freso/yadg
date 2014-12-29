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

from django.template import Context
import django.template.loader
import os


class Formatter(object):

    release_title_template = 'release_title.txt'
    
    def __init__(self,template_dir='output_formats'):
        self._template_dir = template_dir

    def _render_template(self, template, data):
        #we render the description without autoescaping
        c = Context(data,autoescape=False)
        #t.render() returns a django.utils.safestring.SafeData instance which
        #would not be escaped if used in another template. We don't want that,
        #so create a plain unicode string from the return value
        return unicode(template.render(c))

    def title_from_ReleaseResult(self, release_result):
        t = django.template.loader.get_template(os.path.join(self._template_dir,self.release_title_template))
        return self._render_template(t, {'result': release_result})