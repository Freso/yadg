from descgen.forms import InputForm, SettingsForm
from descgen.mixins import CreateTaskMixin, GetFormatMixin
from descgen.scraper.factory import SCRAPER_ITEMS
from .visitor.misc import DescriptionVisitor
from .visitor.template import TemplateVisitor

from django.shortcuts import render, redirect
from django.http import Http404,HttpResponse
from django.views.generic.base import View
from django.views.generic.edit import FormView
from django.views.generic.base import TemplateView

from djcelery.models import TaskMeta

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
        return render(request,'index.html', {'input_form':form})


class ResultView(View):
    
    def get(self, request, id):
        try:
            task = TaskMeta.objects.get(task_id=id)
        except TaskMeta.DoesNotExist:
            return render(request,'result_404.html', status=404)
        if task.status == 'SUCCESS':
            (result, additional_data) = task.result
            visitor = TemplateVisitor(self.request, additional_data, id)

            return visitor.visit(result)

        elif task.status == 'FAILURE' or task.status == 'REVOKED':
            return render(request, 'result_failed.html')
        else:
            return render(request, 'result_waiting.html')


class DownloadResultView(View, GetFormatMixin):
    
    def get(self, request, id, format, title):
        try:
            task = TaskMeta.objects.get(task_id=id)
        except TaskMeta.DoesNotExist:
            raise Http404
        format_cleaned = self.get_valid_format(format)
        if task.status != 'SUCCESS' or format_cleaned != format:
            raise Http404
        visitor = DescriptionVisitor(description_format=format_cleaned)
        try:
            result = visitor.visit(task.result[0])
        except visitor.WrongResultType:
            raise Http404
        response = HttpResponse(result,mimetype='text/plain; charset=utf-8')
        return response
    

class SettingsView(FormView,GetFormatMixin,CreateTaskMixin):
    form_class = SettingsForm
    template_name = 'settings.html'
    
    def get_initial(self):
        initial = {
            'scraper': self.get_valid_scraper(None),
            'description_format': self.get_valid_format(None)
        }
        return initial
    
    def form_valid(self, form):
        self.request.session['default_format'] = form.cleaned_data['description_format']
        self.request.session['default_scraper'] = form.cleaned_data['scraper']
        return render(self.request,self.template_name,{'form':form, 'successful':True})


class ScrapersView(TemplateView):
    template_name = 'scrapers_overview.html'

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


def csrf_failure(request, reason=""):
    return render(request, 'csrf_failure.html', status=403)