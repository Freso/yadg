# coding=utf-8
import json
import datetime
from .base import Scraper, ExceptionMixin, RequestMixin, StandardFactory
from ..result import ReleaseResult, NotFoundResult


READABLE_NAME = 'Bandcamp'
SCRAPER_URL = 'http://www.bandcamp.com/'
NOTES = u'Currently no searching capabilities. Featuring artists on tracks not supported. Only **direct** links to albums are supported (`http://something.bandcamp.com/album/something`).'


class ReleaseScraper(Scraper, ExceptionMixin, RequestMixin):

    base_url = 'http://api.bandcamp.com/api/'
    api_key = ''

    forced_response_encoding = 'utf8'

    string_regex = '^(http(?:s)?://\S+?/album/\S*)$'

    def __init__(self, album_url):
        super(ReleaseScraper, self).__init__()
        self.album_url = album_url

    def get_instance_info(self):
        return u'url=%s' % self.album_url

    def parse_response_content(self, response_content):
        try:
            response = json.loads(response_content)
        except:
            self.raise_exception(u'invalid server response')
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


class ScraperFactory(StandardFactory):

    scraper_classes = [ReleaseScraper]