from descgen.forms import InputForm,FormatForm,SettingsForm
from descgen.formatter import Formatter,FORMATS
from descgen.mixins import CreateTaskMixin,GetDescriptionMixin
from descgen.reverse import reverse

from django.shortcuts import render
from django.http import Http404,HttpResponse, HttpResponseRedirect
from django.views.generic.base import View
from django.views.generic.edit import FormView

from djcelery.models import TaskMeta


class IndexView(View, CreateTaskMixin):
    
    def get(self, request):
        form = InputForm(self.request.GET)
        if form.is_valid():
            input = form.cleaned_data['input']
            scraper = form.cleaned_data['scraper']
            
            task = self.create_task(input=input, scraper=scraper)

            return HttpResponseRedirect(reverse('get_result', kwargs={'id':task.task_id}, request=self.request))
        else:
            form = InputForm(initial={'scraper':self.get_valid_scraper(None)})
        return render(request,'index.html',{'input_form':form})


class ResultView(View, GetDescriptionMixin, CreateTaskMixin):
    
    def get(self, request, id):
        try:
            task = TaskMeta.objects.get(task_id=id)
        except TaskMeta.DoesNotExist:
            return render(request,'result_404.html', status=404)
        if task.status == 'SUCCESS':
            (type,data,additional_data) = task.result
            
            if not additional_data['scraper']:
                additional_data['scraper'] = self.get_valid_scraper(None)
            input_form = InputForm(initial=additional_data)
            
            if type == 'release':
                form = FormatForm(self.request.GET)
                if form.is_valid():
                    format = form.cleaned_data['description_format']
                else:
                    format = None
                
                (format,result) = self.get_formatted_description(data,format)
                
                format_form = FormatForm(initial={'description_format':format})
                
                return render(request,'result.html',{'result':result, 'result_id':id, 'format_form':format_form, 'format':format, 'input_form':input_form})
            elif type == 'list':
                return render(request,'result_list.html',{'scraper_results':data,'input_form':input_form})
            elif type == '404':
                return render(request,'result_id_not_found.html',{'input_form':input_form})
        elif task.status == 'FAILURE' or task.status == 'REVOKED':
            return render(request,'result_failed.html')
        else:
            return render(request,'result_waiting.html')


class DownloadResultView(View):
    
    def get(self, request, id, format):
        try:
            task = TaskMeta.objects.get(task_id=id)
        except TaskMeta.DoesNotExist:
            raise Http404
        if task.status != 'SUCCESS' or task.result[0] != 'release' or not format in FORMATS:
            raise Http404
        data = task.result[1]
        formatter = Formatter()
        result = formatter.format(data,format)
        filename = formatter.get_filename(data)
        response = HttpResponse(result,mimetype='text/plain; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="%s.txt"' % filename if filename else str(id + '-' + format)
        return response
    

class SettingsView(FormView,GetDescriptionMixin,CreateTaskMixin):
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