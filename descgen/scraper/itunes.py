# coding=utf-8
import lxml.html
import re
import json
from .base import Scraper, ExceptionMixin, RequestMixin, UtilityMixin, LoggerMixin, StatusCodeError, StandardFactory
from .base import SearchScraper as SearchScraperBase
from ..result import ReleaseResult, ListResult, NotFoundResult


READABLE_NAME = 'iTunes Store'
SCRAPER_URL = 'http://itunes.apple.com/'


class ReleaseScraper(Scraper, RequestMixin, ExceptionMixin, UtilityMixin, LoggerMixin):

    _base_url = 'http://itunes.apple.com/%s/album/'
    string_regex = '^http(?:s)?://itunes\.apple\.com/(\w{2,4})/album/([^/]*)/([^\?]+)[^/]*$'

    exclude_genres = ['music']

    def __init__(self, store, release_name, id):
        super(ReleaseScraper, self).__init__()
        self.id = id
        self.store = store
        self._release_name = release_name

    def get_instance_info(self):
        return u'id=%s, store=%s' % (self.id, self.store)

    def get_url(self):
        return self._base_url % self.store + self._release_name + '/' + self.id

    def get_params(self):
        return {'ign-mpt': 'uo%3D4'}

    def _split_artists(self, artist_string):
        artists = re.split('(?:,\s?)|&', artist_string)
        artists = map(self.remove_whitespace, artists)
        return artists

    def _check_if_release_artist_equals_track_artist(self):
        #we have to check if the track artist of each track equals the release artist
        artist_h2 = self.parsed_response.cssselect('div#title h2')
        track_artist_tds = self.parsed_response.cssselect('div.center-stack > div.track-list table.tracklist-table tbody tr.song.music td.artist')
        self._release_artist_equal_track_artists = False
        if len(artist_h2) == 1:
            release_artist = artist_h2[0].text_content()
            release_artist = self.remove_whitespace(release_artist)
            for track_artist_td in track_artist_tds:
                self._release_artist_equal_track_artists = release_artist == self.remove_whitespace(
                    track_artist_td.text_content())
                if not self._release_artist_equal_track_artists:
                    break

    def prepare_response_content(self, content):
        #get the raw response content and parse it
        self.parsed_response = lxml.html.document_fromstring(content)

    def add_release_event(self):
        release_date_span = self.parsed_response.cssselect('div#left-stack li.release-date span.label')
        if len(release_date_span) != 1:
            self.log(self.DEBUG, u'could not find release date span')
            release_date_span = self.parsed_response.cssselect('div#left-stack li.expected-release-date span.label')
            if len(release_date_span) != 1:
                self.log(self.WARNING, u'could not find release date span nor expected release date span')
        if len(release_date_span) == 1:
            release_date = release_date_span[0].tail
            release_date = self.remove_whitespace(release_date)
            if release_date:
                release_event = self.result.create_release_event()
                release_event.set_date(release_date)
                self.result.append_release_event(release_event)
            else:
                self.log(self.DEBUG, u'found release date span, but removing whitespace resulted in empty string')

    def add_release_title(self):
        title_h1 = self.parsed_response.cssselect('div#title h1')
        if len(title_h1) != 1:
            self.raise_exception(u'could not find release title h1')
        title = title_h1[0].text_content()
        title = self.remove_whitespace(title)
        if title:
            self.result.set_title(title)

    def add_release_artists(self):
        artist_h2 = self.parsed_response.cssselect('div#title h2')
        if len(artist_h2) != 1:
            self.raise_exception(u'could not find artist h2')
        artist_h2 = artist_h2[0]
        if artist_h2.text_content() == 'Various Artists':
            artist = self.result.create_artist()
            artist.set_various(True)
            artist.append_type(self.result.ArtistTypes.MAIN)
            self.result.append_release_artist(artist)
        else:
            artist_anchors = artist_h2.cssselect('a')
            for anchor in artist_anchors:
                artist_string = anchor.text_content()
                artist_strings = self._split_artists(artist_string)
                for artist_name in artist_strings:
                    artist = self.result.create_artist()
                    artist.set_name(artist_name)
                    artist.append_type(self.result.ArtistTypes.MAIN)
                    self.result.append_release_artist(artist)

    def add_genres(self):
        genre_anchors = self.parsed_response.cssselect('div#left-stack li.genre a')
        for genre_anchor in genre_anchors:
            genre = genre_anchor.text_content()
            genre = self.remove_whitespace(genre)
            if not genre.lower() in self.exclude_genres:
                self.result.append_genre(genre)

    def get_disc_containers(self):
        discs = {}
        tracklist_trs = self.parsed_response.cssselect('table.tracklist-table tbody tr.song.music')
        for tracklist_tr in tracklist_trs:
            children = tracklist_tr.getchildren()
            if len(children) != 6:
                continue
            if not children[0].attrib.has_key('sort-value'):
                continue
            sort_value = children[0].attrib['sort-value']
            m = re.match('(\d+)\d{3}',sort_value)
            if not m:
                continue
            disc_num = int(m.group(1))
            if not disc_num in discs:
                discs[disc_num] = []
            discs[disc_num].append(tracklist_tr)
        return discs

    def get_track_number(self, trackContainer):
        track_num_span = trackContainer.cssselect('td.index span.index span')
        if len(track_num_span) != 1:
            # the track index might be in the name column
            track_num_span = trackContainer.cssselect('td.name span.index span')
            if len(track_num_span) != 1:
                self.raise_exception(u'could not get track number span')
        track_num = track_num_span[0].text_content()
        track_num = self.remove_whitespace(track_num)
        if track_num:
            return track_num
        return None

    def get_track_artists(self, trackContainer):
        track_artists = []
        if not self._release_artist_equal_track_artists:
            track_artist_as = trackContainer.cssselect('td.artist a')
            for track_artist_a in track_artist_as:
                artist_string = track_artist_a.text_content()
                if 'viewCollaboration' in track_artist_a.attrib['href']:
                    # if it is a link to a Collaboration we assume that there are multiple artists that need to be split
                    artist_strings = self._split_artists(artist_string)
                    for artist_name in artist_strings:
                        artist = self.result.create_artist()
                        artist.set_name(artist_name)
                        artist.append_type(self.result.ArtistTypes.MAIN)
                        track_artists.append(artist)
                else:
                    artist = self.result.create_artist()
                    artist.set_name(self.remove_whitespace(artist_string))
                    artist.append_type(self.result.ArtistTypes.MAIN)
                    track_artists.append(artist)
        return track_artists

    def get_track_title(self, trackContainer):
        track_title_span = trackContainer.cssselect('td.name span span.text')
        if len(track_title_span) != 1:
            self.raise_exception(u'could not find track title td')
        track_title = track_title_span[0].text_content()
        track_title = self.remove_whitespace(track_title)
        if track_title:
            return track_title
        return None

    def get_track_length(self, trackContainer):
        track_length_td = trackContainer.cssselect('td.time')
        if len(track_length_td) != 1:
            self.raise_exception(u'could not find track length td')
        track_length = track_length_td[0].text_content()
        track_length = self.remove_whitespace(track_length)
        if track_length:
            return self.seconds_from_string(track_length)
        return None

    def add_discs(self):
        disc_containers = self.get_disc_containers()
        for disc_nr in disc_containers:
            disc = self.result.create_disc()
            disc.set_number(disc_nr)

            for track_container in disc_containers[disc_nr]:
                track = disc.create_track()
                track_number = self.get_track_number(track_container)
                if track_number:
                    track.set_number(track_number)
                track_title = self.get_track_title(track_container)
                if track_title:
                    track.set_title(track_title)
                track_length = self.get_track_length(track_container)
                if track_length:
                    track.set_length(track_length)
                track_artists = self.get_track_artists(track_container)
                for track_artist in track_artists:
                    track.append_artist(track_artist)

                disc.append_track(track)
            self.result.append_disc(disc)

    def get_result(self):
        try:
            response = self.request_get(self.get_url())
        except StatusCodeError as e:
            if str(e) == "404":
                self.result = NotFoundResult()
                self.result.set_scraper_name(self.get_name())
                return self.result
            else:
                self.raise_exception("request to server unsuccessful, status code: %s" % str(e))

        self.prepare_response_content(self.get_response_content(response))

        #if the release does not exist, the website wants to connect to iTunes
        warning_div = self.parsed_response.cssselect('div.loadingbox')
        if len(warning_div) == 1:
            self.result = NotFoundResult()
            self.result.set_scraper_name(self.get_name())
            return self.result

        self._check_if_release_artist_equals_track_artist()

        self.result = ReleaseResult()
        self.result.set_scraper_name(self.get_name())

        self.add_release_event()

        self.add_release_title()

        self.add_release_artists()

        self.add_genres()

        self.add_discs()

        release_url = self.get_original_string()
        if not release_url:
            release_url = self.get_url()
        if release_url:
            self.result.set_url(release_url)

        return self.result


class SearchScraper(SearchScraperBase, RequestMixin, ExceptionMixin):

    url = 'http://itunes.apple.com/search'

    def get_params(self):
        return {'media': 'music', 'entity': 'album', 'limit': '25', 'term': self.search_term}

    def prepare_response_content(self, content):
        try:
            self.parsed_response = json.loads(content)
        except:
            self.raise_exception(u'invalid server response')

    def get_release_containers(self):
        if 'results' in self.parsed_response:
            return self.parsed_response['results']
        return []

    def get_release_name(self, release_container):
        components = []
        for key in ['artistName', 'collectionName']:
            if key in release_container:
                components.append(release_container[key])
        name = u' \u2013 '.join(components)
        return name

    def get_release_info(self, release_container):
        components = []
        if 'releaseDate' in release_container:
            components.append(release_container['releaseDate'].split('T')[0])
        for key in ['country', 'primaryGenreName']:
            if key in release_container:
                components.append(release_container[key])
        info = u' | '.join(components)
        return info

    def get_release_url(self, releaseContainer):
        release_url = None
        if 'collectionViewUrl' in releaseContainer:
            release_url = releaseContainer['collectionViewUrl']
            m = re.match(ReleaseScraper.string_regex, release_url)
            if not m:
                release_url = None
        return release_url

    def get_result(self):
        response = self.request_get(url=self.url, params=self.get_params())
        self.prepare_response_content(self.get_response_content(response))

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
                list_item.set_url(release_url)
                result.append_item(list_item)
        return result


class ScraperFactory(StandardFactory):

    scraper_classes = [ReleaseScraper]
    search_scraper = SearchScraper