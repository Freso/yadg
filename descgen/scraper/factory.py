import discogs, musicbrainz, beatport, metalarchives, audiojelly, junodownload, itunes, bandcamp

_SCRAPERS = {
    'discogs':discogs,
    'musicbrainz':musicbrainz,
    'beatport':beatport,
    'metalarchives':metalarchives,
    'audiojelly':audiojelly,
    'junodownload':junodownload,
    'itunes':itunes,
    'bandcamp':bandcamp,
}

_SCRAPER_RELEASES = dict(map(lambda x: (x,_SCRAPERS[x].Release),filter(lambda x: hasattr(_SCRAPERS[x],'Release'),_SCRAPERS)))

_SCRAPER_RELEASES_SORTED = _SCRAPER_RELEASES.values()
_SCRAPER_RELEASES_SORTED.sort(lambda x,y: cmp(x.priority, y.priority))

_SCRAPER_SEARCHES = dict(map(lambda x: (x,_SCRAPERS[x].Search),filter(lambda x: hasattr(_SCRAPERS[x],'Search'),_SCRAPERS)))

SCRAPER_ITEMS = map(lambda x: {'name': _SCRAPERS[x].READABLE_NAME,
                               'url': _SCRAPERS[x].SCRAPER_URL,
                               'release': hasattr(_SCRAPERS[x], 'Release'),
                               'searchable': hasattr(_SCRAPERS[x], 'Search')}, sorted(_SCRAPERS))

SCRAPER = _SCRAPER_SEARCHES.keys()

SCRAPER_CHOICES = map(lambda x: (x,_SCRAPERS[x].READABLE_NAME),SCRAPER)
SCRAPER_CHOICES.sort(lambda x,y: cmp(x[0],y[0]))

SCRAPER_DEFAULT = 'discogs'

SCRAPER_EXCEPTIONS = (
    discogs.DiscogsAPIError,
    musicbrainz.MusicBrainzAPIError,
    beatport.BeatportAPIError,
    metalarchives.MetalarchivesAPIError,
    audiojelly.AudiojellyAPIError,
    junodownload.JunodownloadAPIError,
    itunes.iTunesAPIError,
    bandcamp.BandcampAPIError,
)


class ScraperFactoryError(Exception):
    pass


class ScraperFactory(object):
    
    def get_release_by_url(self,url):
        release = None
        
        for scraper in _SCRAPER_RELEASES_SORTED:
            release = scraper.release_from_url(url)
            if release:
                break
        
        return release
    
    def get_search(self,search_term,scraper = SCRAPER_DEFAULT):
        if not scraper:
            scraper = SCRAPER_DEFAULT
        if not scraper in SCRAPER:
            raise ScraperFactoryError, u'no searchable scraper "%s"' % scraper
        
        search = _SCRAPER_SEARCHES[scraper](search_term)
        if not getattr(search,'SCRAPER',False):
            setattr(search,'SCRAPER',scraper)
        
        return search

    @staticmethod
    def get_valid_scraper(scraper):
        if not scraper in SCRAPER:
            scraper = SCRAPER_DEFAULT
        return scraper