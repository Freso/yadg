from celery.decorators import task
from descgen.discogs import Search,Release,DiscogsAPIError

@task
def get_search_results(term):
    search = Search(term)
    return ('list',search.releases)

@task
def get_release_info(id):
    release = Release(id)
    try:
        return ('release',release.data)
    except DiscogsAPIError as e:
        if e.message == "404":
            return ('404', None)
        else:
            raise e

@task
def get_release_from_url(url):
    release = Release.release_from_url(url)
    try:
        return ('release',release.data)
    except DiscogsAPIError as e:
        if e.message == "404":
            return ('404', None)
        else:
            raise e