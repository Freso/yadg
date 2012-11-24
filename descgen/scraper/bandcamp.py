# coding=utf-8
import json,datetime
from base import BaseRelease, BaseAPIError


READABLE_NAME = 'Bandcamp'
SCRAPER_URL = 'http://www.bandcamp.com/'
NOTES = u'Currently no searching capabilities. Featuring artists on tracks not supported. Only **direct** links to albums are supported (`http://something.bandcamp.com/album/something`).'


class BandcampAPIError(BaseAPIError):
    pass


class Release(BaseRelease):

    base_url = 'http://api.bandcamp.com/api/'
    api_key = ''

    priority = 15

    exception = BandcampAPIError

    url_regex = '^(http(?:s)?://.*?/album/.*)$'

    def __init__(self, album_url):
        self.album_url = album_url

    def __unicode__(self):
        return u'<BandcampRelease: url=%s>' % self.album_url

    def get_url(self):
        return self.base_url + 'url/1/info'

    def get_params(self):
        return {'url':self.album_url, 'key':self.api_key}

    def _get_band_info(self, band_id):
        r2 = self._make_request(self.REQUEST_METHOD_GET, self.base_url + 'band/3/info', {'band_id':band_id, 'key':self.api_key}, self.get_headers(), None, {})
        if r2.status_code != 200:
            self.raise_request_exception('%d' % (r2.status_code if r2.status_code else 500))

        try:
            resp2 = json.loads(r2.text)
        except:
            self.raise_exception(u'invalid server response')

        if not resp2.has_key('error') or not resp2['error']:
            return resp2
        else:
            self.raise_exception(u'could not get band info')


    def prepare_response_content(self, content):
        try:
            response = json.loads(content)
        except:
            self.raise_exception(u'invalid server response')

        if not response.has_key('album_id'):
            self.raise_request_exception('404')
        else:
            r1 = self._make_request(self.REQUEST_METHOD_GET, self.base_url + 'album/2/info', {'album_id':response['album_id'], 'key':self.api_key}, self.get_headers(), None, {})
            if r1.status_code != 200:
                self.raise_request_exception('%d' % (r1.status_code if r1.status_code else 500))
            else:
                try:
                    resp1 = json.loads(r1.text)
                except:
                    self.raise_exception(u'invalid server response')
                if not resp1.has_key('error') or not resp1['error']:
                    self.parsed_response_album = resp1

        if not hasattr(self, 'parsed_response_album'):
            self.raise_exception('something happened that should not happen')

    def get_release_date(self):
        if self.parsed_response_album.has_key('release_date'):
            date = datetime.datetime.fromtimestamp(self.parsed_response_album['release_date'])
            release_date = unicode(date.year)
            return release_date
        return None

    def get_release_format(self):
        if self.parsed_response_album.has_key('downloadable'):
            if self.parsed_response_album['downloadable'] == 1:
                format = 'Free WEB release'
            else:
                format = 'WEB release'
            return format
        return None

    def get_release_title(self):
        if self.parsed_response_album.has_key('title'):
            return self.parsed_response_album['title']
        return None

    def get_release_artists(self):
        artist = None
        if self.parsed_response_album.has_key('artist'):
            artist = self.parsed_response_album['artist']
        elif self.parsed_response_album.has_key('band_id'):
            band_info = self._get_band_info(self.parsed_response_album['band_id'])
            if band_info.has_key('name'):
                artist = band_info['name']
        if artist:
            return [self.format_artist(artist, self.ARTIST_TYPE_MAIN)]
        return []

    def get_disc_containers(self):
        if self.parsed_response_album.has_key('tracks'):
            return {1:self.parsed_response_album['tracks']}
        return {}

    def get_track_containers(self, discContainer):
        discContainer.sort(lambda x,y: cmp(x['number'], y['number']))
        return discContainer

    def get_track_number(self, trackContainer):
        return str(trackContainer['number'])

    def get_track_artists(self, trackContainer):
        if trackContainer.has_key('artist'):
            return [self.format_artist(trackContainer['artist'], self.ARTIST_TYPE_MAIN)]
        return []

    def get_track_title(self, trackContainer):
        if trackContainer.has_key('title'):
            return trackContainer['title']
        return None

    def get_track_length(self, trackContainer):
        if trackContainer.has_key('duration'):
            m, s = divmod(trackContainer['duration'], 60)
            return u"%d:%02d" % (m, s)
        return None