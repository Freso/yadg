from celery.decorators import task
from descgen.scraper.factory import SCRAPER_EXCEPTIONS

@task
def get_search_results(search,scraper):
    return ('list',(scraper,search.releases))

@task
def get_release_info(release):
    try:
        return ('release',release.data)
    except SCRAPER_EXCEPTIONS as e:
        if str(e) == "404":
            return ('404', None)
        else:
            raise e