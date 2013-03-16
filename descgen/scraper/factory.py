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

_SCRAPER_RELEASES = {}
_SCRAPER_SEARCHES = {}
SCRAPER_ITEMS = []
SCRAPER_CHOICES = []

for scraper_key in sorted(_SCRAPERS):
    scraper = _SCRAPERS[scraper_key]
    has_release = hasattr(scraper, 'Release')
    has_search = hasattr(scraper, 'Search')
    readable_name = scraper.READABLE_NAME
    url = scraper.SCRAPER_URL
    if has_release:
        _SCRAPER_RELEASES[scraper_key] = scraper.Release
    if has_search:
        _SCRAPER_SEARCHES[scraper_key] = scraper.Search
        # the scraper is searchable, so add it to the list of scraper choices used by the forms
        SCRAPER_CHOICES.append((scraper_key, readable_name))
    scraper_item = {
        'name': readable_name,
        'url': url,
        'release': has_release,
        'searchable': has_search
    }
    if hasattr(scraper, 'NOTES'):
        scraper_item['notes'] = scraper.NOTES
    SCRAPER_ITEMS.append(scraper_item)

_SCRAPER_RELEASES_SORTED = _SCRAPER_RELEASES.values()
_SCRAPER_RELEASES_SORTED.sort(lambda x,y: cmp(x.priority, y.priority))

SCRAPER = _SCRAPER_SEARCHES.keys()

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