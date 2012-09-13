from descgen.forms import InputForm,FormatForm,SettingsForm
from descgen.mixins import CreateTaskMixin,GetDescriptionMixin

from django.shortcuts import render,redirect
from django.http import Http404,HttpResponse
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
                
            return redirect('get_result',id=task.task_id)
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
                release_title = self.get_formatted_release_title(data)
                
                format_form = FormatForm(initial={'description_format':format})
                
                return render(request,'result.html',{'result':result, 'result_id':id, 'release_title':release_title, 'additional_data':additional_data, 'format_form':format_form, 'format':format, 'input_form':input_form})
            elif type == 'list':
                return render(request,'result_list.html',{'scraper_results':data, 'additional_data':additional_data, 'input_form':input_form})
            elif type == '404':
                return render(request,'result_id_not_found.html',{'input_form':input_form})
        elif task.status == 'FAILURE' or task.status == 'REVOKED':
            return render(request,'result_failed.html')
        else:
            return render(request,'result_waiting.html')


class DownloadResultView(View, GetDescriptionMixin):
    
    def get(self, request, id, format, title):
        try:
            task = TaskMeta.objects.get(task_id=id)
        except TaskMeta.DoesNotExist:
            raise Http404
        format_cleaned = self.get_valid_format(format)
        if task.status != 'SUCCESS' or task.result[0] != 'release' or format_cleaned != format:
            raise Http404
        data = task.result[1]
        (format, result) = self.get_formatted_description(data, format)
        response = HttpResponse(result,mimetype='text/plain; charset=utf-8')
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

def csrf_failure(request, reason=""):
    return render(request, 'csrf_failure.html', status=403)