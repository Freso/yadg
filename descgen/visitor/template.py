#!/usr/bin/python
# -*- coding: utf-8 -*-

from .base import Visitor
from ..forms import InputForm, FormatForm
from ..formatter import Formatter
from ..mixins import GetFormatMixin, CreateTaskMixin
from ..models import Template

from django.shortcuts import render


class TemplateVisitor(Visitor, GetFormatMixin, CreateTaskMixin):

    def __init__(self, request, additional_data, result_id):
        super(TemplateVisitor, self).__init__()

        self.request = request
        self.additional_data = additional_data
        self.result_id = result_id
        self.formatter = Formatter()

        if not self.additional_data['scraper']:
            self.additional_data['scraper'] = self.get_valid_scraper(None)
        self.input_form = InputForm(initial=self.additional_data)

    def visit_NotFoundResult(self, result):
        return render(self.request, 'result_id_not_found.html', {'input_form': self.input_form})

    def visit_ListResult(self, result):
        return render(self.request, 'result_list.html', {'result': result, 'additional_data': self.additional_data, 'input_form': self.input_form})

    def visit_ReleaseResult(self, result):
        form = FormatForm(self.request.user, self.request.GET)
        if form.is_valid():
            format = form.cleaned_data['template']
            try:
                format = Template.objects.get(pk=format)
            except Template.DoesNotExist:
                temp = Template.templates_for_user(self.request.user, with_utility=False)
                if temp:
                    format = temp[0]
                else:
                    format = None
        else:
            temp = Template.templates_for_user(self.request.user, with_utility=False)
            if temp:
                format = temp[0]
            else:
                format = None

        #format = self.get_valid_format(format)
        release_title = self.formatter.title_from_ReleaseResult(release_result=result)

        format_form = form # FormatForm(initial={'description_format': format})

        dependencies = {}
        if format:
            for dep in format.cached_dependencies_set(prefetch_owner=True):
                dependencies[dep.get_unique_name()] = dep

        import json
        from .misc import JSONSerializeVisitor
        v = JSONSerializeVisitor()
        data = v.visit(result)

        return render(self.request, 'result.html',{'result_id': self.result_id, 'release_title':release_title, 'additional_data': self.additional_data, 'format_form': format_form, 'format': format, 'input_form': self.input_form,
                                                   'json_data': json.dumps(data), 'template':format, 'dependencies':dependencies})