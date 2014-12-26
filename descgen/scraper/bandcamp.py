# coding=utf-8
import secret
import json
import datetime
from .base import Scraper, ExceptionMixin, RequestMixin, StandardFactory
from ..result import ReleaseResult, NotFoundResult, ListResult


READABLE_NAME = 'Bandcamp'
SCRAPER_URL = 'http://www.bandcamp.com/'
NOTES = u'YADG cannot search for releases on Bandcamp, you will always need to enter the exact link. Additionally, ' \
        u"links to Bandcamp artists or albums are only picked up automatically if the URL contains the string " \
        u"`/album/` or `.bandcamp.com`. In all other cases you need to force the use of the Bandcamp scraper by " \
        u"choosing it from the drop down menu (this will result in the input being interpreted as a Bandcamp URL)."


_API_KEY = secret.BANDCAMP_API_KEY


class ReleaseScraper(Scraper, ExceptionMixin, RequestMixin):

    base_url = 'http://api.bandcamp.com/api/'
    api_key = _API_KEY

    forced_response_encoding = 'utf8'

    string_regex = '^(http(?:s)?://\S+?/album/\S*)$'

    VARIOUS_ARTISTS_ALIASES = ['various artists']

    def __init__(self, album_url):
        super(ReleaseScraper, self).__init__()
        self.album_url = album_url

    def get_instance_info(self):
        return u'url=%s' % self.album_url

    def parse_response_content(self, response_content):
        try:
            response = json.loads(response_content)
        except:
            self.raise_exception(u'invalid server response: %r' % response_content)
        return response

    def add_release_event(self):
        if 'release_date' in self.album_response:
            release_event = self.result.create_release_event()
            date = datetime.datetime.fromtimestamp(self.album_response['release_date'])
            release_date = unicode(date.year)
            release_event.set_date(release_date)
            self.result.append_release_event(release_event)

    def add_release_format(self):
        if 'downloadable' in self.album_response:
            if self.album_response['downloadable'] == 1:
                format = 'Free WEB release'
            else:
                format = 'WEB release'
            self.result.set_format(format)

    def add_release_title(self):
        if 'title' in self.album_response:
            self.result.set_title(self.album_response['title'])

    def add_release_artists(self):
        artist_name = None
        if 'artist' in self.album_response:
            artist_name = self.album_response['artist']
        elif 'band_id' in self.album_response:
            response = self.request_get(url=self.base_url + 'band/3/info', params={'band_id': self.album_response['band_id'], 'key': self.api_key})
            band_info_response = self.parse_response_content(self.get_response_content(response))
            if 'error' in band_info_response and band_info_response['error']:
                self.raise_exception(u'could not get band info')
            elif 'name' in band_info_response:
                artist_name = band_info_response['name']
        if artist_name:
            artist = self.result.create_artist()
            if artist_name.lower() in self.VARIOUS_ARTISTS_ALIASES:
                artist.set_various(True)
            else:
                artist.set_name(artist_name)
            artist.append_type(self.result.ArtistTypes.MAIN)
            self.result.append_release_artist(artist)

    def add_discs(self):
        if 'tracks' in self.album_response:
            disc = self.result.create_disc()
            disc.set_number(1)

            tracks = self.album_response['tracks']
            tracks.sort(lambda x,y: cmp(x['number'], y['number']))
            for track_container in tracks:
                track = disc.create_track()
                if 'number' in track_container:
                    track.set_number(str(track_container['number']))
                if 'title' in track_container:
                    track.set_title(track_container['title'])
                if 'duration' in track_container:
                    track.set_length(int(round(track_container['duration'])))
                if 'artist' in track_container:
                    track_artist = self.result.create_artist()
                    track_artist.set_name(track_container['artist'])
                    track_artist.append_type(self.result.ArtistTypes.MAIN)
                    track.append_artist(track_artist)

                disc.append_track(track)
            self.result.append_disc(disc)

    def get_result(self):
        # we don't care to catch any StatusCode exceptions here, if the status code of the api call is not equal to 200
        # then something is wrong with the api
        response = self.request_get(url=self.base_url + 'url/1/info', params={'url': self.album_url, 'key': self.api_key})

        # if we got no album ID, we cannot find the release
        album_discovery_response = self.parse_response_content(self.get_response_content(response))
        if not 'album_id' in album_discovery_response:
            self.result = NotFoundResult()
            self.result.set_scraper_name(self.get_name())
            return self.result

        # again: we don't catch a status code error
        response = self.request_get(url=self.base_url + 'album/2/info', params={'album_id': album_discovery_response['album_id'], 'key': self.api_key})

        self.album_response = self.parse_response_content(self.get_response_content(response))

        # the api could not give us the album
        if 'error' in self.album_response and self.album_response['error']:
            self.result = NotFoundResult()
            self.result.set_scraper_name(self.get_name())
            return self.result

        self.result = ReleaseResult()
        self.result.set_scraper_name(self.get_name())

        self.add_release_event()

        self.add_release_format()

        self.add_release_title()

        self.add_release_artists()

        self.add_discs()

        release_url = self.get_original_string()
        if not release_url:
            release_url = self.album_url
        if release_url:
            self.result.set_url(release_url)

        return self.result


class DiscographyScraper(Scraper, ExceptionMixin, RequestMixin):

    base_url = 'http://api.bandcamp.com/api/'
    api_key = _API_KEY

    forced_response_encoding = 'utf8'

    string_regex = '^(http(?:s)?://\S+?\.bandcamp\.com(?:/\S*)?)$'

    def __init__(self, search_term):
        super(DiscographyScraper, self).__init__()
        self.band_url = search_term

    def get_instance_info(self):
        return u'band_url=%s' % self.band_url

    def parse_response_content(self, response_content):
        try:
            response = json.loads(response_content)
        except:
            self.raise_exception(u'invalid server response')
        return response

    def get_release_containers(self):
        if 'discography' in self.discography_response:
            return self.discography_response['discography']
        else:
            return []

    def get_release_name(self, release_container):
        components = []
        if 'artist' in release_container:
            components.append(release_container['artist'])
        if 'title' in release_container:
            components.append(release_container['title'])
        release_name = u' \u2013 '.join(components)
        if release_name:
            return release_name
        return None

    def get_release_url(self, release_container):
        if 'url' in release_container and '/album/' in release_container['url']:
            return release_container['url']
        return None

    def get_release_info(self, release_container):
        if 'release_date' in release_container:
            try:
                date = datetime.datetime.fromtimestamp(release_container['release_date'])
            except ValueError:
                date = None
            if date:
                date_string = date.strftime('%Y-%m-%d')
                return 'Release date: %s' % date_string
        return None

    def get_result(self):
        # we don't care to catch any StatusCode exceptions here, if the status code of the api call is not equal to 200
        # then something is wrong with the api
        response = self.request_get(url=self.base_url + 'url/1/info', params={'url': self.band_url, 'key': self.api_key})

        # if we got no band ID, we cannot find the discography
        band_discovery_response = self.parse_response_content(self.get_response_content(response))
        if not 'band_id' in band_discovery_response:
            result = NotFoundResult()
            result.set_scraper_name(self.get_name())
            return result
        band_id = band_discovery_response['band_id']

        # again: we don't catch a status code error
        response = self.request_get(url=self.base_url + 'band/3/discography', params={'band_id': band_id, 'key': self.api_key})
        self.discography_response = self.parse_response_content(self.get_response_content(response))

        result = ListResult()
        result.set_scraper_name(self.get_name())

        release_containers = self.get_release_containers()
        for release_container in release_containers:
            release_name = self.get_release_name(release_container)
            release_url = self.get_release_url(release_container)

            # we only add releases to the result list that we can actually access
            if release_url is not None and release_name is not None:
                release_info = self.get_release_info(release_container)

                list_item = result.create_item()
                list_item.set_name(release_name)
                list_item.set_info(release_info)
                list_item.set_query(release_url)
                list_item.set_query_scraper(self.get_name())
                list_item.set_url(release_url)
                result.append_item(list_item)
        return result


class ScraperFactory(StandardFactory):

    scraper_classes = [ReleaseScraper, DiscographyScraper]
    search_scraper = DiscographyScraper

    def is_searchable(self):
        return False