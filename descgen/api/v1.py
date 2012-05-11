from djangorestframework.views import View
from djangorestframework.response import Response,ErrorResponse
from djangorestframework import status
from djangorestframework.resources import FormResource
from djangorestframework.mixins import ResponseMixin
from djangorestframework.renderers import BaseRenderer,JSONPRenderer

from django.core.urlresolvers import reverse
from django.utils.http import urlencode

from descgen.forms import InputForm,ResultForm
from descgen.scraper.factory import SCRAPER_CHOICES
from descgen.formatter import FORMAT_CHOICES
from descgen.mixins import CreateTaskMixin,GetDescriptionMixin

from djcelery.models import TaskMeta


class GETFormResource(FormResource):
    """
    A special form resource, that allows for additional special get parameters
    """
    
    def validate_request(self, data, files=None):
        """
        Overwritten method to allow for the special fields.
        """
        
        return self._validate(data, files,allowed_extra_fields=(BaseRenderer._FORMAT_QUERY_PARAM,JSONPRenderer.callback_parameter,ResponseMixin._ACCEPT_QUERY_PARAM,'stupid_ie'))


class InputFormResource(GETFormResource):
    form = InputForm


class FormatFormResource(GETFormResource):
    form = ResultForm

class Root(View):
    """
    This is the entry point to the rest of the YADG API.
    
    All the APIs allow anonymous access, and can be navigated either through the browser or from the command line...
    
        $ curl -X GET http://yadg.cc/api/v1/                           # (Use default renderer)
        $ curl -X GET http://yadg.cc/api/v1/ -H 'Accept: text/plain'   # (Use plaintext documentation renderer)
    
    The renderer can be chosen by standard HTTP accept header negotiation. A list of available renderers can be obtained by calling...
    
        $ curl -X OPTIONS http://yadg.cc/api/v1/ -H 'Accept: text/plain'
    
    The renderer can be overridden by providing an additional `format` GET parameter.
    
    For `json-p` requests the optional GET parameter `callback` specifies the used callback function:
    
        $ curl -X GET http://yadg.cc/api/v1/?callback=use_this_callback -H 'Accept: application/json-p'
    """

    def get(self, request):
        return [{'name': 'Format List', 'url': reverse('api_v1_formatlist')},
                {'name': 'Scraper List', 'url': reverse('api_v1_scraperlist')},
                {'name': 'Make Query', 'url': reverse('api_v1_makequery')},
                ]


class ScraperList(View,CreateTaskMixin):
    """
    This returns a list of all available scrapers.
    
    It can be used to populate a scraper select box like this:
    
        <select>
            <option value="value[0]">name[0]</option>
            ...
        </select>
    
    `default` specifies what scraper will be used if the scraper parameter is omitted on a query.
    
    **Note:** If the request includes a valid session cookie as set by the main site this api call will respect the saved defaults if any.
    """
    
    def get(self, request):
        default_scraper = self.get_valid_scraper(None)
        return Response(content=map(lambda x: {'value': x[0], 'name': x[1], 'default':x[0]==default_scraper},SCRAPER_CHOICES))


class FormatList(View,GetDescriptionMixin):
    """
    This returns a list of all available description formats.
    
    It can be used to populate a format select box like this:
    
        <select>
            <option value="value[0]">name[0]</option>
            ...
        </select>
    
    `default` specifies what description format will be used if the format parameter is omitted on a result query.
    
    **Note:** If the request includes a valid session cookie as set by the main site this api call will respect the saved defaults if any.
    """

    def get(self, request):
        default_format = self.get_valid_format(None)
        return Response(content=map(lambda x: {'value': x[0], 'name': x[1], 'default':x[0]==default_format},FORMAT_CHOICES))


class MakeQuery(View, CreateTaskMixin):
    """
    This initiates a new query with the given parameters and returns the url for getting the result.
    
    `input` can either be a search term or an explicit url to the release page of a supported scraper. If it is the latter any scraper provided with `scraper` will be ignored.
    
    If `input` is a search term and `scraper` is omitted the default scraper will be used.
    
    It returns the following fields:
    
    * `result_url` contains the api call for obtaining the result of the query.
    * `result_id` contains only the unique identifier for the result. This is only needed if the client has to construct some url involving the id itself.
    
    **Note:** If the request includes a valid session cookie as set by the main site this api call will respect the saved defaults if any.
    """
     
    resource = InputFormResource
    
    def get_name(self):
        return "Make Query"
    
    def get(self, request):
        input = self.PARAMS['input']
        scraper = self.PARAMS['scraper']
        
        task = self.create_task(input=input, scraper=scraper)
        
        result = {
            'result_url': reverse('api_v1_result',args=[task.task_id]),
            'result_id': task.task_id
        }
        
        return Response(content=result)
    
    def post(self, request):
        params = urlencode(self.CONTENT)
        return Response(status.HTTP_303_SEE_OTHER, headers={'Location':reverse('api_v1_makequery')+'?'+params})


class Result(View, GetDescriptionMixin):
    """
    This returns the result of a query.
    
    ***Important:*** Results of queries are purged periodically. Clients cannot assume that the current result will be available forever.
    
    If `status == 'waiting'` then the query has not yet been completed and the client should poll again in the future.
    
    If `status == 'failed'` then the query could not be completed successfully. As this might be due to a temporary error the client is advised to repeat its query.
    
    If `status == 'done'` then the server completed the query without an error and depending on the `type` the client can expect specific fields to be present in the response.
    
    If the query resulted in obtaining a specific release `type` will be `'release'` and the following fields will be present:
    
    * `description_format` contains the format of the rendered description. This can be set by including `description_format=FORMAT` in the api call. If this parameter is not present the default format will be used.
    * `description` contains the rendered description.
    * if `include_raw_data=True` is specified then `raw_data` will contain the raw data as returned by the scraper
    
    If the query returned a list of releases `type` will be `'release_list'` and the following fields will be present:
    
    * `releases` contains a mapping `scraper => releases returned by the scraper`. In the release list each entry has a field `query_url` that contains the api call needed for querying for this exact release. **Note:** `releases` is empty if the search yielded no results.
    * `release_count` contains the number of releases that were found by the scrapers. If no release was found this will be `0`.
    
    If the query tried to obtain a specific release but failed because it could not be found `type` will be `'release_not_found'`. The response will contain no further fields.
    
    **Note:** the parameters `include_raw_data` and `description_format` are ignored for all but `'release'`-Type results.
    
    **Note (2):** If the request includes a valid session cookie as set by the main site this api call will respect the saved defaults if any.
    """
    
    resource = FormatFormResource
    
    def get_name(self):
        return "Result"
    
    def get(self, request, id):
        try:
            task = TaskMeta.objects.get(task_id=id)
        except TaskMeta.DoesNotExist:
            return Response(status.HTTP_404_NOT_FOUND)
            
        format = self.PARAMS['description_format']
        include_raw_data = self.PARAMS['include_raw_data']
        
        result = {}
        
        if task.status == 'SUCCESS':
            result['status'] = 'done'
            
            (type,data,additional_data) = task.result
            if type == 'release':
                result['type'] = 'release'

                (format,description) = self.get_formatted_description(data, format)
                
                result['description'] = description
                result['description_format'] = format
                
                if include_raw_data:
                    # we have to make sure that there are no non-string keys in the dict
                    for potential in ('discs', 'discTitles'):
                        if data.has_key(potential):
                            keys = data[potential].keys()
                            max_digits = len(str(len(keys)))
                            for key in keys:
                                data[potential]['disc_' + str(key).zfill(max_digits)] = data[potential][key]
                                del data[potential][key]
                    result['raw_data'] = data;
            elif type == 'list':
                result['type'] = 'release_list'
                
                release_count = 0;
                
                for releases in data.values():
                    for entry in releases:
                        entry['release_url'] = entry['release'].release_url
                        entry['query_url'] = reverse('api_v1_makequery') + '?' + urlencode({'input':entry['release'].release_url})
                        del entry['release']
                        release_count += 1
                
                result['releases'] = data
                result['release_count'] = release_count
            elif type == '404':
                result['type'] = 'release_not_found'
        elif task.status == 'FAILURE' or task.status == 'REVOKED':
            result['status'] = 'failed'
        else:
            result['status'] = 'waiting'
        return Response(content=result)
            
    def post(self, request, id):
        params = urlencode(self.CONTENT)
        return Response(status.HTTP_303_SEE_OTHER, headers={'Location':reverse('api_v1_result', args=(id,))+'?'+params})