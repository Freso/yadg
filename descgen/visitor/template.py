#!/usr/bin/python
# -*- coding: utf-8 -*-

from .base import Visitor
from ..forms import InputForm
from ..formatter import Formatter
from ..mixins import GetFormatMixin, CreateTaskMixin, GetTemplateMixin, SerializeResultMixin

from django.shortcuts import render


class TemplateVisitor(Visitor, GetFormatMixin, CreateTaskMixin, GetTemplateMixin, SerializeResultMixin):

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
        template, form = self.get_template_and_form()

        release_title = self.get_release_title(release_result=result)

        dependencies = self.get_all_dependencies(template, prefetch_owner=True)

        # TODO: namespace the release data to avoid conflicts at a later date
        data = self.serialize_to_json(result)

        return render(self.request, 'result.html',{'result_id': self.result_id, 'release_title':release_title, 'additional_data': self.additional_data, 'format_form': form, 'input_form': self.input_form,
                                                   'json_data': data, 'template':template, 'dependencies':dependencies})