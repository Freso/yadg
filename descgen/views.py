from descgen.forms import InputForm,FormatForm
from descgen.tasks import get_search_results,get_release_info
from descgen.formatter import Formatter,FORMATS,FORMAT_DEFAULT
from descgen.scraper.factory import ScraperFactory

from django.shortcuts import render,redirect
from django.http import Http404,HttpResponse
from django.views.generic.base import View

from djcelery.models import TaskMeta


class IndexView(View):
    
    def get(self, request):
        form = InputForm(self.request.GET)
        if form.is_valid():
            factory = ScraperFactory()
            input = form.cleaned_data['input']
            scraper = form.cleaned_data['scraper']
            release = factory.get_release_by_url(input)
            if release:
                task = get_release_info.delay(release)
            else:
                task = get_search_results.delay(factory.get_search(input,scraper))
            #make sure a TaskMeta object for the created task exists
            TaskMeta.objects.get_or_create(task_id=task.task_id)
                
            return redirect('get_result',id=task.task_id)
        else:
            form = InputForm()
        return render(request,'index.html',{'input_form':form})


class ResultView(View):
    
    def get(self, request, id):
        try:
            task = TaskMeta.objects.get(task_id=id)
        except TaskMeta.DoesNotExist:
            return render(request,'result_404.html', status=404)
        if task.status == 'SUCCESS':
            (type,data) = task.result
            if type == 'release':
                form = FormatForm(self.request.GET)
                
                if form.is_valid():
                    format = form.cleaned_data['description_format']
                else:
                    format = FORMAT_DEFAULT
                    
                formatter = Formatter()
                
                result = formatter.format(data,format)
                
                format_form = FormatForm(initial={'description_format':format})
                
                return render(request,'result.html',{'result':result,'result_id':id, 'format_form':format_form,'format':format,'result_id':id})
            elif type == 'list':
                return render(request,'result_list.html',{'scraper_results':data})
            elif type == '404':
                return render(request,'result_id_not_found.html')
        elif task.status == 'FAILURE' or task.status == 'REVOKED':
            return render(request,'result_failed.html', status=503)
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
    