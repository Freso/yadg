from descgen.scraper.factory import ScraperFactory,SCRAPER_DEFAULT
from descgen.formatter import Formatter,FORMAT_DEFAULT
from descgen.tasks import get_search_results,get_release_info

from djcelery.models import TaskMeta


class CreateTaskMixin(object):
    
    factory = ScraperFactory()
    
    def create_task(self, **kwargs):
        input = kwargs['input']
        scraper = kwargs['scraper']
        
        scraper = self.get_valid_scraper(scraper)
        
        release = self.factory.get_release_by_url(input)
        if release:
            task = get_release_info.delay(release,kwargs)
        else:
            task = get_search_results.delay(self.factory.get_search(input,scraper),kwargs)
        #make sure a TaskMeta object for the created task exists
        TaskMeta.objects.get_or_create(task_id=task.task_id)
        
        return task
    
    def get_valid_scraper(self, scraper):
        if not scraper:
            scraper = self.request.session.get("default_scraper", SCRAPER_DEFAULT)
        scraper = self.factory.get_valid_scraper(scraper)
        
        return scraper


class GetDescriptionMixin(object):
    
    formatter = Formatter()
    
    def get_formatted_description(self, data, format):
        format = self.get_valid_format(format)
        
        return (format,self.formatter.format(data,format))

    def get_formatted_release_title(self, data):
        return self.formatter.get_release_title(data)

    def get_valid_format(self, format):
        if not format:
            format = self.request.session.get("default_format", FORMAT_DEFAULT)
        format = self.formatter.get_valid_format(format)
        
        return format