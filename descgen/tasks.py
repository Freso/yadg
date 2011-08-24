from celery.decorators import task
from descgen.discogs import Search,Release

@task
def get_search_results(term):
    search = Search(term)
    return ('list',search.releases)

@task
def get_release_info(id):
    release = Release(id)
    return ('release',release.data)

@task
def get_release_from_url(url):
    release = Release.release_from_url(url)
    return ('release',release.data)