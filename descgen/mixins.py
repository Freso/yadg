from .scraper.factory import ScraperFactory
from .formatter import Formatter
from .tasks import get_result
from .models import Settings, Template
from .forms import FormatForm
from .visitor.misc import JSONSerializeVisitor, CheckReleaseResultVisitor

from djcelery.models import TaskMeta

import json


class GetSettingsMixin(object):

    def get_settings(self, test=lambda x: True):
        settings = None
        if self.request.user.is_authenticated():
            try:
                settings = self.request.user.settings
            except Settings.DoesNotExist:
                pass

        if settings is None or not test(settings):
            try:
                settings = Settings.objects.get(user__isnull=True)
            except Settings.DoesNotExist:
                pass
        return settings


class CreateTaskMixin(GetSettingsMixin):
    
    factory = ScraperFactory()
    
    def create_task(self, **kwargs):
        input = kwargs['input']
        scraper_name = kwargs['scraper']
        
        scraper_name = self.get_valid_scraper(scraper_name)
        
        scraper = self.factory.get_scraper_by_string(input)
        if not scraper:
            scraper = self.factory.get_search_scraper(input, scraper_name)

        task = get_result.delay(scraper, kwargs)
        #make sure a TaskMeta object for the created task exists
        TaskMeta.objects.get_or_create(task_id=task.task_id)
        
        return task
    
    def get_valid_scraper(self, scraper):
        if not scraper:
            settings = self.get_settings(test=lambda x: x.default_scraper)
            if settings is not None:
                scraper = settings.default_scraper
        scraper = self.factory.get_valid_scraper(scraper)
        
        return scraper


class GetTemplateMixin(GetSettingsMixin):

    with_utility = False

    def get_with_utility(self):
        return self.with_utility

    def get_template_form_data(self):
        return self.request.GET

    def get_template_form_user(self):
        return self.request.user

    def get_default_template(self):
        template = None
        settings = self.get_settings(test=lambda x: x.default_template)
        if settings is not None:
            template = settings.default_template
        return template

    def get_template_and_form(self, with_utility=None):
        if with_utility is None:
            with_utility = self.get_with_utility()
        form = FormatForm(self.get_template_form_user(), self.get_template_form_data(), with_utility=with_utility)
        if form.is_valid():
            template_id = form.cleaned_data['template']
            try:
                template = Template.objects.get(pk=template_id)
            except Template.DoesNotExist:
                # this actually can only happen in case of a very unfortunate race condition
                template = None
        else:
            template = self.get_default_template()
            form = FormatForm(self.get_template_form_user(), default_template=template, with_utility=with_utility)
        return template, form

    def get_all_dependencies(self, template, prefetch_owner=False):
        dependencies = {}
        for dep in template.cached_dependencies_set(prefetch_owner=prefetch_owner):
                dependencies[self.get_dependency_name(dep)] = dep
        return dependencies

    def get_dependency_name(self, dependency):
        return dependency.get_unique_name()

    def get_immediate_dependencies(self, template, prefetch_owner=False):
        dependencies = template.dependencies.all()
        if prefetch_owner:
            dependencies = dependencies.select_related('owner')
        return dependencies


class GetReleaseTitleMixin(object):
    
    formatter = Formatter()

    def get_release_title(self, release_result):
        return self.formatter.title_from_ReleaseResult(release_result=release_result)


class SerializeResultMixin(object):

    serializer = JSONSerializeVisitor()
    json_kwargs = {}
    data_namespace = 'data'

    def serialize_to_json(self, result, additional_data={}, json_kwargs=None):
        data = self.serializer.visit(result)
        if self.get_data_namespace():
            data = self._namespace_result(data)
        data.update(additional_data)
        if json_kwargs is None:
            json_kwargs = self.get_json_kwargs()
        return json.dumps(data, **json_kwargs)

    def get_json_kwargs(self):
        return self.json_kwargs

    def get_data_namespace(self):
        return self.data_namespace

    def _namespace_result(self, result):
        return {self.get_data_namespace(): result}


class CheckResultMixin(object):

    release_checker = CheckReleaseResultVisitor()

    def is_release_result(self, result):
        return self.release_checker.visit(result)