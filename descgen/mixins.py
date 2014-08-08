from .scraper.factory import ScraperFactory
from .formatter import Formatter, FORMAT_DEFAULT
from .tasks import get_result
from .models import Settings

from djcelery.models import TaskMeta


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

    def get_default_template(self):
        template = None
        settings = self.get_settings(test=lambda x: x.default_template)
        if settings is not None:
            template = settings.default_template
        return template


class GetFormatMixin(object):
    
    formatter = Formatter()

    def get_valid_format(self, format):
        if not format:
            format = self.request.session.get("default_format", FORMAT_DEFAULT)
        format = self.formatter.get_valid_format(format)
        
        return format