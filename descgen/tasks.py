from celery.decorators import task
from descgen.scraper.factory import SCRAPER_EXCEPTIONS

@task
def get_search_results(search, additional_data):
    if not getattr(search,'__iter__',False):
        search = [search,]
    result = {}
    for s in search:
        if len(s.releases) > 0:
            result[s.SCRAPER] = s.releases
    return ('list',result,additional_data)

@task
def get_release_info(release, additional_data):
    try:
        return ('release',release.data,additional_data)
    except SCRAPER_EXCEPTIONS as e:
        if unicode(e).startswith(u"404"):
            return ('404', None, None)
        else:
            raise e