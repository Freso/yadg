# Create your views here.
from descgen.forms import InputForm
from descgen.discogs import Release
from descgen.tasks import get_release_from_url,get_search_results,get_release_info
from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.template import Context
from djcelery.models import TaskMeta
import django.template.loader
import json

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
            #make sure a TaskMeta object for the created task exists
            TaskMeta.objects.get_or_create(task_id=task.task_id)
            if request.GET.has_key("xhr"):
                return HttpResponse(task.task_id)
            else:
                return redirect('get_result',id=task.task_id)
        elif request.GET.has_key("xhr"):
            #we have an ajax request, but we are missing a required field
            return HttpResponse(status=400)
    else:
        form = InputForm()
    return render(request,'index.html',{'form':form})

def get_by_discogs_id(request,id):
    task = get_release_info.delay(int(id))
    #make sure a TaskMeta object for the created task exists
    TaskMeta.objects.get_or_create(task_id=task.task_id)
    if request.GET.has_key("xhr"):
        return HttpResponse(task.task_id)
    else:
        return redirect('get_result',id=task.task_id)

def get_result(request,id):
    try:
        task = TaskMeta.objects.get(task_id=id)
    except TaskMeta.DoesNotExist:
        if request.GET.has_key("xhr"):
            return HttpResponse(status=404)
        return render(request,'result_404.html',{'form':InputForm()}, status=404)
    if task.status == 'SUCCESS':
        (type,data) = task.result
        if type == 'release':
            t = django.template.loader.get_template('result_template.txt')
            c = Context(data)
            result = t.render(c)
            if request.GET.has_key("xhr"):
                return HttpResponse(json.dumps(('result',result),ensure_ascii=False))
            return render(request,'result.html',{'result':result,'form':InputForm()})
        elif type == 'list':
            if request.GET.has_key("xhr"):
                for entry in data:
                    entry['release'] = entry['release'].id
                return HttpResponse(json.dumps(('list',data),ensure_ascii=False))
            return render(request,'result_list.html',{'release_list':data,'form':InputForm()})
        elif type == '404':
            if request.GET.has_key("xhr"):
                return HttpResponse(json.dumps(('notfound',[]),ensure_ascii=False))
            return render(request,'result_not_found_on_discogs.html', {'form':InputForm()})
    elif task.status == 'FAILURE' or task.status == 'REVOKED':
        if request.GET.has_key("xhr"):
            return HttpResponse(status=503)
        return render(request,'result_failed.html', {'form':InputForm()}, status=503)
    else:
        if request.GET.has_key("xhr"):
                return HttpResponse(json.dumps(('waiting',[]),ensure_ascii=False))
        return render(request,'result_waiting.html')