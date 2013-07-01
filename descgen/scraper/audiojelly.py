# coding=utf-8
import lxml.html
import re
from .base import Scraper, ExceptionMixin, RequestMixin, UtilityMixin, StatusCodeError, StandardFactory
from .base import SearchScraper as SearchScraperBase
from ..result import ReleaseResult, ListResult, NotFoundResult


READABLE_NAME = 'Audiojelly'
SCRAPER_URL = 'http://www.audiojelly.com/'


class ReleaseScraper(Scraper, RequestMixin, ExceptionMixin, UtilityMixin):

    _base_url = 'http://www.audiojelly.com/'
    string_regex = '^http://(?:www\.)?audiojelly\.com/releases/(.*?)/(\d+)$'

    _various_artists_aliases = ['Various', 'Various Artists']

    def __init__(self, id, release_name):
        super(ReleaseScraper, self).__init__()
        self.id = id
        self._release_name = release_name

    def get_instance_info(self):
        return u'id=%d, name="%s"' % (self.id, self._release_name)

    @staticmethod
    def _get_args_from_match(match):
        return int(match.group(2)), match.group(1)

    def get_url(self):
        return self._base_url + 'releases/%s/%d' % (self._release_name, self.id)

    def _separate_multiple_artists(self, artist_string):
        artists = re.split('(?i)\\s*?(?:,|&|with|pres.)\\s*?', artist_string)
        artists = map(self.remove_whitespace, artists)
        return artists

    def _split_artists(self, artist_string):
        artists = re.split('(?i)\\s*?(?:ft\\.?|feat\\.?|featuring)\\s*?', artist_string)
        main_artists = self._separate_multiple_artists(artists[0])
        featuring_artists = []
        if len(artists) > 1:
            for featuring_artist_string in artists[1:]:
                featuring_artists += self._separate_multiple_artists(featuring_artist_string)
        return main_artists, featuring_artists

    def prepare_response_content(self, content):
        #get the raw response content and parse it
        self.parsed_response = lxml.html.document_fromstring(content)

        self._label_dict = dict(map(lambda x: (x.getprevious().text_content().lower(), x),filter(lambda x: x.getprevious() is not None,self.parsed_response.cssselect('label + span.spec'))))
        self._track_artists_equal_release_artist = True

        # check if the artists of each track equal the release artists
        if 'artist' in self._label_dict:
            release_artists = self._label_dict['artist'].text_content()
            release_artists = self.remove_whitespace(release_artists)

            track_artists = self.parsed_response.cssselect('span.artistName')
            for track_artist_span in track_artists:
                track_artist = track_artist_span.text_content()
                track_artist = self.remove_whitespace(track_artist)
                self._track_artists_equal_release_artist = track_artist == release_artists
                if not self._track_artists_equal_release_artist:
                    break

    def add_release_event(self):
        if 'release date' in self._label_dict:
            release_date = self._label_dict['release date'].text_content()
            release_date = self.remove_whitespace(release_date)
            if release_date:
                release_event = self.result.create_release_event()
                release_event.set_date(release_date)
                self.result.append_release_event(release_event)

    def add_label_ids(self):
        if 'cat number' in self._label_dict:
            cat_number = self._label_dict['cat number'].text_content()
            cat_number = self.remove_whitespace(cat_number)
        if 'label' in self._label_dict:
            label_anchors = self._label_dict['label'].cssselect('a')
            for anchor in label_anchors:
                link_text = anchor.text_content()
                link_text = self.remove_whitespace(link_text)
                if link_text:
                    label_id = self.result.create_label_id()
                    label_id.set_label(link_text)
                    if cat_number:
                        label_id.append_catalogue_nr(cat_number)
                    self.result.append_label_id(label_id)

    def add_release_title(self):
        title_h1 = self.parsed_response.cssselect('div.pageHeader h1')
        if len(title_h1) == 1:
            title_h1 = title_h1[0]
            title = title_h1.text_content()
            title = self.remove_whitespace(title)
            if title:
                self.result.set_title(title)
        else:
            self.raise_exception(u'could not determine title h1')

    def add_release_artists(self):
        if 'artist' in self._label_dict:
            artist_anchors = self._label_dict['artist'].cssselect('a')
            for anchor in artist_anchors:
                artist = anchor.text_content()
                artist = self.remove_whitespace(artist)
                if artist:
                    if artist in self._various_artists_aliases:
                        artist = self.result.create_artist()
                        artist.set_various(True)
                        artist.append_type(self.result.ArtistTypes.MAIN)
                        self.result.append_release_artist(artist)
                    else:
                        main_artists, featuring_artists = self._split_artists(artist)
                        for main_artist in main_artists:
                            artist = self.result.create_artist()
                            artist.set_name(main_artist)
                            artist.append_type(self.result.ArtistTypes.MAIN)
                            self.result.append_release_artist(artist)
                        for featuring_artist in featuring_artists:
                            artist = self.result.create_artist()
                            artist.set_name(featuring_artist)
                            artist.append_type(self.result.ArtistTypes.FEATURING)
                            self.result.append_release_artist(artist)
        else:
            self.raise_exception(u'could not find artist span')

    def add_genres(self):
        if 'genre' in self._label_dict:
            genre_anchors = self._label_dict['genre'].cssselect('a')
            for anchor in genre_anchors:
                genre_string = anchor.text_content()
                genre_string = self.remove_whitespace(genre_string)
                if genre_string:
                    genres = re.split('\\s*?(?:/|,)\\s*?', genre_string)
                    genres = filter(lambda x: x, genres)
                    for genre in genres:
                        self.result.append_genre(genre)

    def get_tracklist_elem(self):
        release_tracklist = self.parsed_response.cssselect('div.trackList.release')
        if len(release_tracklist) != 1:
            self.raise_exception(u'could not get track list div')
        return release_tracklist[0]

    def get_track_containers(self, tracklist_elem):
        return tracklist_elem.cssselect('div.trackListRow')

    def get_track_number(self, track_container):
        track_number = track_container.cssselect('p.trackNum')
        if len(track_number) == 1:
            track_number = track_number[0].text_content()
            track_number = self.remove_whitespace(track_number)
            if track_number:
                track_number = track_number.lstrip('0')
                if not track_number:
                    track_number = '0'
                return track_number
        self.raise_exception(u'could not get track number')

    def get_track_artists(self, track_container):
        artists = []
        if not self._track_artists_equal_release_artist:
            artist_span = track_container.cssselect('span.artistName')
            if len(artist_span) == 1:
                artist_anchors = artist_span[0].cssselect('a')
                for anchor in artist_anchors:
                    artist = anchor.text_content()
                    artist = self.remove_whitespace(artist)
                    if artist and not artist in self._various_artists_aliases:
                        main_artists, featuring_artists = self._split_artists(artist)
                        for track_main_artist in main_artists:
                            artist = self.result.create_artist()
                            artist.set_name(track_main_artist)
                            artist.append_type(self.result.ArtistTypes.MAIN)
                            artists.append(artist)
                        for track_featuring_artist in featuring_artists:
                            artist = self.result.create_artist()
                            artist.set_name(track_featuring_artist)
                            artist.append_type(self.result.ArtistTypes.FEATURING)
                            artists.append(artist)
        return artists

    def get_track_title(self, track_container):
        title_span = track_container.cssselect('span.trackName')
        if len(title_span) == 1:
            title = title_span[0].text_content()
            title = self.remove_whitespace(title)
            if title:
                return title
        self.raise_exception(u'could not get track title')

    def get_track_length(self, track_container):
        length_span = track_container.cssselect('span.trackTime')
        if len(length_span) == 1:
            length_string = length_span[0].text_content()
            length_string = self.remove_whitespace(length_string)
            if length_string:
                i = 0
                length = 0
                for component in reversed(length_string.split(':')):
                    length += int(component) * 60**i
                    i += 1
                return length
        return None

    def add_discs(self):
        tracklist_elem = self.get_tracklist_elem()
        disc = self.result.create_disc()
        disc.set_number(1)

        for track_container in self.get_track_containers(tracklist_elem):
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

        self.result = ReleaseResult()
        self.result.set_scraper_name(self.get_name())

        self.prepare_response_content(self.get_response_content(response))

        self.add_release_event()

        self.add_label_ids()

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


class SearchScraper(SearchScraperBase, RequestMixin, ExceptionMixin, UtilityMixin):

    _base_url = 'http://www.audiojelly.com'
    url = _base_url + '/search/all/'

    _not_found = False

    def get_params(self):
        return {'view': 'releases', 'q': self.search_term}

    def prepare_response_content(self, content):
        #get the raw response content and parse it
        self.parsed_response = lxml.html.document_fromstring(content)

    def get_release_containers(self):
        return self.parsed_response.cssselect('div.relInfo')[:25]

    def get_release_name_and_url(self, release_container):
        release_artist_anchor = release_container.cssselect('div.relArtistName a')
        if len(release_artist_anchor) == 0:
            self.raise_exception(u'could not extract release artist')
        artists = []
        for artist_anchor in release_artist_anchor:
            artist = artist_anchor.text_content()
            artist = self.remove_whitespace(artist)
            if artist:
                artists.append(artist)
        release_title_anchor = release_container.cssselect('div.relReleaseName a')
        if len(release_title_anchor) != 1:
            self.raise_exception(u'could not get release name anchor')
        release_title = release_title_anchor[0].text_content()
        release_title = self.remove_whitespace(release_title)
        release_url = self._base_url + release_title_anchor[0].attrib['href']
        m = re.match(ReleaseScraper.string_regex, release_url)
        if not m:
            release_url = None
        return u', '.join(artists) + u' \u2013 ' + release_title, release_url

    def get_release_info(self, release_container):
        components = []
        label_div = release_container.cssselect('div.relLabel')
        if len(label_div) == 1:
            label = label_div[0].text_content()
            label = self.remove_whitespace(label)
            if label:
                components.append(label)
        genre_div = release_container.cssselect('div.relGenre')
        if len(genre_div) == 1:
            genre = genre_div[0].text_content()
            genre = self.remove_whitespace(genre)
            if genre:
                components.append(genre)
        if components:
            return u' | '.join(components)
        return None

    def get_result(self):

        try:
            response = self.request_get(url=self.url, params=self.get_params())
        except StatusCodeError as e:
            # Warning: The following is ugly hack territory. The stupid site apparently returns a 500 status code if it cannot
            # find at least one release with the given search term.
            # So instead of raising an exception with a 500 status code, we return an empty result
            if str(e) == '500':
                result = ListResult()
                result.set_scraper_name(self.get_name())
                return result
            else:
                raise e

        self.prepare_response_content(self.get_response_content(response))

        result = ListResult()
        result.set_scraper_name(self.get_name())

        release_containers = self.get_release_containers()
        for release_container in release_containers:
            release_name, release_url = self.get_release_name_and_url(release_container)

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