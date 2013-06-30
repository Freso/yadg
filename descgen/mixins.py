from .scraper.factory import ScraperFactory, SCRAPER_DEFAULT
from .formatter import Formatter, FORMAT_DEFAULT
from .tasks import get_results

from djcelery.models import TaskMeta


class CreateTaskMixin(object):
    
    factory = ScraperFactory()
    
    def create_task(self, **kwargs):
        input = kwargs['input']
        scraper_name = kwargs['scraper']
        
        scraper_name = self.get_valid_scraper(scraper_name)
        
        scraper = self.factory.get_scraper_by_string(input)
        if not scraper:
            scraper = self.factory.get_search_scraper(input, scraper_name)

        task = get_results.delay(scraper, kwargs)
        #make sure a TaskMeta object for the created task exists
        TaskMeta.objects.get_or_create(task_id=task.task_id)
        
        return task
    
    def get_valid_scraper(self, scraper):
        if not scraper:
            scraper = self.request.session.get("default_scraper", SCRAPER_DEFAULT)
        scraper = self.factory.get_valid_scraper(scraper)
        
        return scraper


class GetFormatMixin(object):
    
    formatter = Formatter()

    def get_valid_format(self, format):
        if not format:
            format = self.request.session.get("default_format", FORMAT_DEFAULT)
        format = self.formatter.get_valid_format(format)
        
        return format