from djangorestframework.views import View
from djangorestframework.response import Response
from djangorestframework import status

from descgen.forms import InputForm,IdQueryForm
from descgen.scraper.factory import ScraperFactory, SCRAPER_CHOICES
from descgen.tasks import get_search_results,get_release_info
from descgen.formatter import FORMAT_CHOICES

from djcelery.models import TaskMeta


class SearchQuery(View):
    
    form = InputForm
    
    def post(self, request):
        factory = ScraperFactory()
        input = self.CONTENT['input']
        scraper = self.CONTENT['scraper']
        release = factory.get_release_by_url(input)
        if release:
            task = get_release_info.delay(release)
        else:
            task = get_search_results.delay(factory.get_search(input,scraper))
        #make sure a TaskMeta object for the created task exists
        TaskMeta.objects.get_or_create(task_id=task.task_id)
        return Response(content={'query_id':task.task_id},status=status.HTTP_201_CREATED)


class IdQuery(View):
    
    form = IdQueryForm
    
    def post(self, request):
        factory = ScraperFactory()
        id = self.CONTENT['id']
        scraper = self.CONTENT['scraper']
        release = factory.get_release_by_id(id,scraper)
        task = get_release_info.delay(release)
        #make sure a TaskMeta object for the created task exists
        TaskMeta.objects.get_or_create(task_id=task.task_id)
        return Response(content={'query_id':task.task_id},status=status.HTTP_201_CREATED)


class ScraperList(View):
    
    def get(self, request):
        return Response(content=SCRAPER_CHOICES)


class FormatList(View):

    def get(self, request):
        return Response(content=FORMAT_CHOICES)


class ResultQuery(View):
    
    def get(self, request, id):
        try:
            task = TaskMeta.objects.get(task_id=id)
        except TaskMeta.DoesNotExist:
            return Response(status.HTTP_404_NOT_FOUND)
        if task.status == 'SUCCESS':
            (type,data) = task.result
            if type == 'release':
                format = request.GET.get('f',FORMAT_DEFAULT)
                if format == 'raw' and request.GET.has_key("xhr"):
                    result = data
                else:
                    formatter = Formatter()
                    format = format if format in FORMATS else FORMAT_DEFAULT
                    result = formatter.format(data,format)
                if request.GET.has_key("xhr"):
                    return HttpResponse(json.dumps(('result',result),ensure_ascii=False), mimetype='application/json; charset=utf-8')
                format_form = FormatForm(initial={'f':format})
                return render(request,'result.html',{'result':result,'format_form':format_form,'format':format,'result_id':id})
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