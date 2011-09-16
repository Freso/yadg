from celery.decorators import task
from descgen.scraper.factory import SCRAPER_EXCEPTIONS

@task
def get_search_results(search):
    if not getattr(search,'__iter__',False):
        search = [search,]
    result = {}
    for s in search:
        if len(s.releases) > 0:
            result[s.SCRAPER] = s.releases
    return ('list',result)

@task
def get_release_info(release):
    try:
        return ('release',release.data)
    except SCRAPER_EXCEPTIONS as e:
        if str(e) == "404":
            return ('404', None)
        else:
            raise e