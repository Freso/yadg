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

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from django.views.generic import View, FormView, TemplateView
from descgen.forms import InputForm, SettingsForm, ApiTokenForm
from descgen.mixins import CreateTaskMixin
from descgen.models import Settings
from descgen.scraper.factory import SCRAPER_ITEMS
from descgen.visitor.template import TemplateVisitor
from djcelery.models import TaskMeta
from rest_framework.authtoken.models import Token
import markdown


class IndexView(View, CreateTaskMixin):

    def get(self, request):
        form = InputForm(self.request.GET)
        if form.is_valid():
            input = form.cleaned_data['input']
            scraper = form.cleaned_data['scraper']

            task = self.create_task(input=input, scraper=scraper)

            return redirect('get_result',id=task.task_id)
        else:
            form = InputForm(initial={'scraper': self.get_valid_scraper(None)})
        return render(request, 'misc/index.html', {'input_form':form})


class ResultView(View):

    def get(self, request, id):
        try:
            task = TaskMeta.objects.get(task_id=id)
        except TaskMeta.DoesNotExist:
            return render(request, 'result/result_404.html', status=404)
        if task.status == 'SUCCESS':
            (result, additional_data) = task.result
            visitor = TemplateVisitor(self.request, additional_data, id)

            return visitor.visit(result)

        elif task.status == 'FAILURE' or task.status == 'REVOKED':
            return render(request, 'result/result_failed.html')
        else:
            return render(request, 'result/result_waiting.html')


class SettingsView(FormView):
    form_class = SettingsForm
    template_name = 'misc/settings.html'

    def get_form_kwargs(self):
        kwargs = super(SettingsView, self).get_form_kwargs()
        try:
            settings = self.request.user.settings
        except Settings.DoesNotExist:
            settings = Settings(user=self.request.user)
        kwargs['instance'] = settings
        return kwargs

    def form_valid(self, form):
        form.save()
        return render(self.request, self.template_name, {'form': form, 'successful': True})

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(SettingsView, self).dispatch(request, *args, **kwargs)


class ScrapersView(TemplateView):
    template_name = 'misc/scrapers_overview.html'

    def get_context_data(self, **kwargs):
        data = super(ScrapersView, self).get_context_data(**kwargs)

        md = markdown.Markdown(output_format='html5', safe_mode='escape')

        scrapers = []

        for scraper in SCRAPER_ITEMS:
            scraper_item = {
                'name': scraper['name'],
                'url': scraper['url'],
                'release': scraper['release'],
                'searchable': scraper['searchable']
            }
            if 'notes' in scraper:
                scraper_item['notes'] = md.convert(scraper['notes'])
            scrapers.append(scraper_item)

        data['scrapers'] = scrapers

        return data


class ApiTokenView(FormView):
    template_name = 'misc/api_token.html'
    form_class = ApiTokenForm

    def get_context_data(self, **kwargs):
        data = super(ApiTokenView, self).get_context_data(**kwargs)
        try:
            data['token'] = self.request.user.auth_token
        except Token.DoesNotExist:
            pass
        return data

    def form_valid(self, form):
        try:
            token = self.request.user.auth_token
        except Token.DoesNotExist:
            pass
        else:
            token.delete()
        Token.objects.create(user=self.request.user)
        return self.render_to_response(self.get_context_data(form=form, created=True))

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(ApiTokenView, self).dispatch(request, *args, **kwargs)




def csrf_failure(request, reason=""):
    return render(request, 'misc/csrf_failure.html', status=403)