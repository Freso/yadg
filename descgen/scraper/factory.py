import descgen.scraper.discogs as discogs
import descgen.scraper.musicbrainz as musicbrainz
import descgen.scraper.beatport as beatport

_SCRAPERS = {
    'discogs':discogs,
    'musicbrainz':musicbrainz,
    'beatport':beatport,
}

_SCRAPER_RELEASES = dict(map(lambda x: (x,_SCRAPERS[x].Release),_SCRAPERS))

_SCRAPER_SEARCHES = dict(map(lambda x: (x,_SCRAPERS[x].Search),_SCRAPERS))

SCRAPER = _SCRAPERS.keys()

SCRAPER_CHOICES = map(lambda x: (x,_SCRAPERS[x].READABLE_NAME),_SCRAPERS)

SCRAPER_DEFAULT = 'discogs'

SCRAPER_EXCEPTIONS = (
    discogs.DiscogsAPIError,
    musicbrainz.MusicBrainzAPIError,
    beatport.BeatportAPIError,
)


class ScraperFactoryError(Exception):
    pass


class ScraperFactory(object):
    
    def get_release_by_id(self,id,scraper):
        if not scraper in SCRAPER:
            raise ScraperFactoryError, u'no scraper "%s"' % scraper
        
        id = _SCRAPER_RELEASES[scraper].id_from_string(id)
        
        return _SCRAPER_RELEASES[scraper](id)
    
    def get_release_by_url(self,url):
        release = None
        
        for scraper in _SCRAPER_RELEASES.values():
            release = scraper.release_from_url(url)
            if release:
                break
        
        return release
    
    def get_search(self,search_term,scraper):
        if not scraper in SCRAPER:
            raise ScraperFactoryError, u'no scraper "%s"' % scraper
        
        search = _SCRAPER_SEARCHES[scraper](search_term)
        if not getattr(search,'SCRAPER',False):
            setattr(search,'SCRAPER',scraper)
        
        return search