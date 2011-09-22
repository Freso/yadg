# Create your views here.
from descgen.forms import InputForm
from descgen.tasks import get_search_results,get_release_info
from django.shortcuts import render,redirect
from django.http import HttpResponse,Http404
from django.template import Context
from djcelery.models import TaskMeta
from django.views.decorators.csrf import csrf_exempt
from descgen.scraper.factory import ScraperFactory,SCRAPER
import django.template.loader
import json

@csrf_exempt
def index(request):
    if request.method == 'POST':
        form = InputForm(request.POST)
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
            if request.GET.has_key("xhr"):
                return HttpResponse(task.task_id, mimetype='text/plain; charset=utf-8')
            else:
                return redirect('get_result',id=task.task_id)
        elif request.GET.has_key("xhr"):
            #we have an ajax request, but we are missing a required field
            return HttpResponse(status=400)
    else:
        form = InputForm()
    return render(request,'index.html',{'input_form':form})

def get_by_id(request,id,scraper):
    if not scraper in SCRAPER:
        raise Http404
    factory = ScraperFactory()
    try:
        #try to get a release with the given id
        release = factory.get_release_by_id(id,scraper)
    except ValueError:
        #the id is malformed
        raise Http404
    task = get_release_info.delay(release)
    #make sure a TaskMeta object for the created task exists
    TaskMeta.objects.get_or_create(task_id=task.task_id)
    if request.GET.has_key("xhr"):
        return HttpResponse(task.task_id, mimetype='text/plain; charset=utf-8')
    else:
        return redirect('get_result',id=task.task_id)

def get_result(request,id):
    try:
        task = TaskMeta.objects.get(task_id=id)
    except TaskMeta.DoesNotExist:
        if request.GET.has_key("xhr"):
            return HttpResponse(status=404)
        return render(request,'result_404.html', status=404)
    if task.status == 'SUCCESS':
        (type,data) = task.result
        if type == 'release':
            format = request.GET.get('f','whatcd')
            if format == 'raw' and request.GET.has_key("xhr"):
                result = data
            else:
                t = django.template.loader.get_template('result_template.txt')
                c = Context(data)
                result = t.render(c)
            if request.GET.has_key("xhr"):
                return HttpResponse(json.dumps(('result',result),ensure_ascii=False), mimetype='application/json; charset=utf-8')
            return render(request,'result.html',{'result':result})
        elif type == 'list':
            if request.GET.has_key("xhr"):
                for releases in data.values():
                    for entry in releases:
                        entry['release'] = entry['release'].id
                return HttpResponse(json.dumps(('list',data),ensure_ascii=False), mimetype='application/json; charset=utf-8')
            return render(request,'result_list.html',{'scraper_results':data})
        elif type == '404':
            if request.GET.has_key("xhr"):
                return HttpResponse(json.dumps(('notfound',[]),ensure_ascii=False), mimetype='application/json; charset=utf-8')
            return render(request,'result_id_not_found.html')
    elif task.status == 'FAILURE' or task.status == 'REVOKED':
        if request.GET.has_key("xhr"):
            return HttpResponse(status=503)
        return render(request,'result_failed.html', status=503)
    else:
        if request.GET.has_key("xhr"):
                return HttpResponse(json.dumps(('waiting',[]),ensure_ascii=False), mimetype='application/json; charset=utf-8')
        return render(request,'result_waiting.html')