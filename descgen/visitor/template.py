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

from .base import Visitor
from ..forms import InputForm
from ..mixins import GetReleaseTitleMixin, CreateTaskMixin, GetTemplateMixin, SerializeResultMixin

from django.shortcuts import render


class TemplateVisitor(Visitor, GetReleaseTitleMixin, CreateTaskMixin, GetTemplateMixin, SerializeResultMixin):

    def __init__(self, request, additional_data, result_id):
        super(TemplateVisitor, self).__init__()

        self.request = request
        self.additional_data = additional_data
        self.result_id = result_id

        if not self.additional_data['scraper']:
            self.additional_data['scraper'] = self.get_valid_scraper(None)
        self.input_form = InputForm(initial=self.additional_data)

    def visit_NotFoundResult(self, result):
        return render(self.request, 'result/result_id_not_found.html', {'input_form': self.input_form})

    def visit_ListResult(self, result):
        return render(self.request, 'result/result_list.html', {'result': result, 'additional_data': self.additional_data, 'input_form': self.input_form})

    def visit_ReleaseResult(self, result):
        template, form = self.get_template_and_form()

        release_title = self.get_release_title(release_result=result)

        dependencies = self.get_all_dependencies(template, prefetch_owner=False)

        data = self.serialize_to_json(result)

        return render(self.request, 'result/result.html',{'result_id': self.result_id, 'release_title':release_title, 'additional_data': self.additional_data, 'format_form': form, 'input_form': self.input_form,
                                                   'json_data': data, 'template':template, 'dependencies':dependencies})