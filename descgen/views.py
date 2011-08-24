# Create your views here.
from descgen.forms import InputForm
from descgen.discogs import Release
from descgen.tasks import get_release_from_url,get_search_results,get_release_info
from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse
from django.template import Context
from djcelery.models import TaskMeta
import django.template.loader

def index(request):
    if request.method == 'POST':
        form = InputForm(request.POST)
        if form.is_valid():
            input = form.cleaned_data['input']
            if Release.release_from_url(input):
                task = get_release_from_url.delay(input)
            else:
                try:
                    id = int(input)
                except:
                    task = get_search_results.delay(input)
                else:
                    task = get_release_info.delay(id)
            if request.GET.has_key("htx"):
                return HttpResponse(task.task_id)
            else:
                return redirect('get_result',id=task.task_id)
    else:
        form = InputForm()
    return render(request,'index.html',{'form':form})

def get_by_discogs_id(request,id):
    task = get_release_info.delay(int(id))
    return redirect('get_result',id=task.task_id)

def get_result(request,id):
    task = get_object_or_404(TaskMeta,task_id__exact=id)
    data = task.result
    t = django.template.loader.get_template('result_template.txt')
    c = Context(data)
    result = t.render(c)
    return render(request,'result.html',{'result':result,'status':task.status})