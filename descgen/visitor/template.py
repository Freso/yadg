#!/usr/bin/python
# -*- coding: utf-8 -*-

from .base import Visitor
from ..forms import InputForm, FormatForm
from ..formatter import Formatter
from ..mixins import GetFormatMixin, CreateTaskMixin

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
        form = FormatForm(self.request.GET)
        if form.is_valid():
            format = form.cleaned_data['description_format']
        else:
            format = None

        format = self.get_valid_format(format)
        release_title = self.formatter.title_from_ReleaseResult(release_result=result)
        description = self.formatter.description_from_ReleaseResult(release_result=result, format=format)

        format_form = FormatForm(initial={'description_format': format})

        import json
        from .api import APIVisitorV1
        v = APIVisitorV1(description_format="whatcd", include_raw_data=True);
        data = v.visit(result);

        return render(self.request, 'result.html',{'description': description, 'result_id': self.result_id, 'release_title':release_title, 'additional_data': self.additional_data, 'format_form': format_form, 'format': format, 'input_form': self.input_form,
                                                   'json_data': json.dumps(data["raw_data"]), 'dot_template':'''{{ for (i in it.artists) { }}{{! it.artists[i].name }}{{? i < it.artists.length-1 }}, {{?}}{{ } }} - {{! it.title }}'''})