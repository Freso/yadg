#!/usr/bin/python
# -*- coding: utf-8 -*-
from descgen.api.v2.serializers import ApiSerializeVisitor
from .serializers import TemplateSerializer, InputSerializer
from ...models import Template
from ...mixins import CreateTaskMixin, GetTemplateMixin, SerializeResultMixin
from ...scraper.factory import SCRAPER_CHOICES
from rest_framework import viewsets
from rest_framework import views
from rest_framework.response import Response
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework import generics
from djcelery.models import TaskMeta


class ApiRootView(views.APIView):
    """
    This is the entry point to the rest of the YADG API.

    All the APIs allow anonymous access, and can be navigated either through the browser or from the command line...

        $ curl -X GET https://yadg.cc/api/v2/                                           # (Use default renderer)
        $ curl -X GET https://yadg.cc/api/v2/ -H 'Accept: application/json; indent=4'   # (Use json renderer with indentation)

    The renderer can be chosen by standard HTTP accept header negotiation. A list of available renderers can be obtained by calling...

        $ curl -X OPTIONS https://yadg.cc/api/v2/ -H 'Accept: application/json'

    The renderer can be overridden by providing an additional `format` GET parameter.

    To authenticate yourself you need to send the `Authorization` header containing your API token. You can obtain your API token [here](https://yadg.cc/api/token) after registering an account. The API token should be prefixed by the string literal "Token", with whitespace separating the two strings. For example:

        Authorization: Token e4595a049538f01f8bb67218e50d91c722cecd03

    An authorized request can then be sent by calling...

        curl -X GET https://yadg.cc/api/v2/ -H 'Authorization: Token e4595a049538f01f8bb67218e50d91c722cecd03'
    """

    def get(self, request):
        return Response({'templates': reverse('api_v2_template-list', request=request),
                         'scrapers': reverse('api_v2_scraper-list', request=request),
                         'query': reverse('api_v2_make-query', request=request)})


class TemplateViewSet(viewsets.ReadOnlyModelViewSet, GetTemplateMixin):
    """
    This returns a paginated list of all templates that are available to you.

    By default a page contains 20 entries. To override this value append the GET parameter `page_size` with the desired number of entries per page (max 100).

    **Note:** To get all your templates including your private ones you must authenticate yourself as described in the API root.
    """

    serializer_class = TemplateSerializer
    paginate_by = 20

    def get_serializer_context(self):
        ctx = super(TemplateViewSet, self).get_serializer_context()
        ctx['default_template'] = self.get_default_template()
        return ctx

    def get_queryset(self):
        return Template.templates_for_user(self.request.user, with_utility=True, sort_by_name=True)


class ScraperViewSet(viewsets.ViewSet, CreateTaskMixin):
    """
    This returns a list of all available scrapers.

    It can be used to populate a scraper select box like this:

        <select>
            <option value="value[0]">name[0]</option>
            ...
        </select>

    `default` specifies what scraper will be used if the scraper parameter is omitted on a query.

    **Note:** If your request is authenticated as described in the API root this API call will respect the saved defaults if any.
    """


    def list(self, request):
        default_scraper = self.get_valid_scraper(None)
        return Response(map(lambda x: {'value': x[0], 'name': x[1], 'default': x[0]==default_scraper}, SCRAPER_CHOICES))


class ResultView(views.APIView, SerializeResultMixin):
    """
    This returns the result of a query.

    ***Important:*** Results of queries are purged periodically. Clients cannot assume that the current result will be available forever.

    If `status == 'waiting'` then the query has not yet been completed and the client should poll again in the future.

    If `status == 'failed'` then the query could not be completed successfully. As this might be due to a temporary error the client is advised to repeat its query.

    If `status == 'done'` then the server completed the query without an error and depending on the `data.type` the client can expect specific fields to be present in the response.

    If the query resulted in obtaining a specific release `data.type` will be `'ReleaseResult'` and `data` will contain the serialized release object.

    If the query returned a list of releases `data.type` will be `'ListResult'` and the following fields will be present:

    * `items` contains the list of scraped items. In this list each entry has a field `queryParams` that contains the necessary query parameters needed for querying for this exact release. **Note:** `items` is empty if the search yielded no results.

    If the query tried to obtain a specific release but failed because it could not be found `data.type` will be `'NotFoundResult'`. The response will contain no further fields.
    """

    serializer = ApiSerializeVisitor()

    def get(self, request, task_id=None):
        try:
            task = TaskMeta.objects.get(task_id=task_id)
        except TaskMeta.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        data = {}

        if task.status == 'SUCCESS':
            (result, additional_data) = task.result
            data = self._namespace_result(self.serializer.visit(result))
            data['status'] = 'done'
        elif task.status == 'FAILURE' or task.status == 'REVOKED':
            data['status'] = 'failed'
        else:
            data['status'] = 'waiting'
        data['url'] = reverse('api_v2_result-detail', kwargs={'task_id': task_id}, request=request)
        return Response(data)


class MakeQueryView(generics.GenericAPIView, CreateTaskMixin):
    """
    This initiates a new query with the given parameters and returns the url for getting the result.

    `input` can either be a search term or an explicit url to the release page of a supported scraper. If it is the latter any scraper provided with `scraper` will be ignored.

    If `input` is a search term and `scraper` is omitted the default scraper will be used.

    It returns the following fields:

    * `url` contains the api call for obtaining the result of the query.
    * `resultId` contains only the unique identifier for the result. This is only needed if the client has to construct some url involving the id itself.

    Requests have to use `POST`. All available parsers can be obtained by calling...

        $ curl -X OPTIONS https://yadg.cc/api/v2/query/ -H 'Accept: application/json'

    **Note:** If your request is authenticated as described in the API root this API call will respect the saved defaults if any.
    """

    serializer_class = InputSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)

        if serializer.is_valid():
            data = serializer.save()

            input = data['input']
            scraper = data['scraper']

            task = self.create_task(input=input, scraper=scraper)

            result = {
                'url': reverse('api_v2_result-detail', kwargs={'task_id': task.task_id}, request=request),
                'resultId': task.task_id
            }

            return Response(result)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
