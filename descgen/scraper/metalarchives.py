# coding=utf-8
import lxml.html
import re
import json
from .base import Scraper, ExceptionMixin, RequestMixin, UtilityMixin, StatusCodeError, StandardFactory
from .base import SearchScraper as SearchScraperBase
from ..result import ReleaseResult, ListResult, NotFoundResult


READABLE_NAME = 'Metal-Archives'
SCRAPER_URL = 'http://www.metal-archives.com/'
NOTES = 'Search terms are only matched against **album titles**. It is *not possible* to search for artists through YADG.'


class ReleaseScraper(Scraper, RequestMixin, ExceptionMixin, UtilityMixin):

    _base_url = 'http://www.metal-archives.com/'
    string_regex = '^http://(?:www\.)?metal-archives\.com/albums/(.*?)/(.*?)/(\d+)$'

    forced_response_encoding = 'utf-8'

    def __init__(self, id, release_artist = '', release_name = ''):
        super(ReleaseScraper, self).__init__()
        self.id = id

        self._release_artist = release_artist
        self._release_name = release_name

        self._info_dict = None

    def get_instance_info(self):
        return u'id=%d' % self.id

    @staticmethod
    def _get_args_from_match(match):
        return int(match.group(3)), match.group(1), match.group(2)

    def get_url(self):
        return self._base_url + 'albums///%d' % self.id

    def get_full_url(self):
        return self._base_url + 'albums/%s/%s/%d' % (self._release_artist, self._release_name, self.id)

    def _get_info_dict(self):
        if self._info_dict is None:
            self._info_dict = {}
            info_dl = self.parsed_response.cssselect('div#album_info dl')
            for dl in info_dl:
                children = dl.getchildren()
                if len(children) % 2 == 1:
                    self.raise_exception(u'album info dl has uneven number of children')
                while children:
                    dt = children[0].text_content()
                    dd = self.remove_whitespace(children[1].text_content())
                    children = children[2:]
                    if dt == 'Type:':
                        self._info_dict['format'] = dd
                    elif dt == 'Release date:':
                        self._info_dict['released'] = dd
                    elif dt == 'Label:':
                        self._info_dict['label'] = dd
        return self._info_dict

    def prepare_response_content(self, content):
        #get the raw response content and parse it
        self.parsed_response = lxml.html.document_fromstring(content)

    def add_release_event(self):
        info_dict = self._get_info_dict()
        if 'released' in info_dict:
            release_event = self.result.create_release_event()
            release_event.set_date(info_dict['released'])
            self.result.append_release_event(release_event)

    def add_release_format(self):
        info_dict = self._get_info_dict()
        if 'format' in info_dict:
            self.result.set_format(info_dict['format'])

    def add_label_ids(self):
        info_dict = self._get_info_dict()
        if 'label' in info_dict:
            label_id = self.result.create_label_id()
            label_id.set_label(info_dict['label'])
            self.result.append_label_id(label_id)

    def add_release_title(self):
        title_h1 = self.parsed_response.cssselect('div#album_info h1.album_name')
        if len(title_h1) != 1:
            self.raise_exception(u'could not find album title h1')
        title_h1 = title_h1[0]
        title = self.remove_whitespace(title_h1.text_content())
        if title:
            self.result.set_title(title)

    def add_release_artists(self):
        artists_h2 = self.parsed_response.cssselect('div#album_info h2.band_name')
        if len(artists_h2) == 0:
            self.raise_exception(u'could not find artist h2')
        for artist_h2 in artists_h2:
            artist_name = self.remove_whitespace(artist_h2.text_content())
            artist = self.result.create_artist()
            artist.set_name(artist_name)
            artist.append_type(self.result.ArtistTypes.MAIN)
            self.result.append_release_artist(artist)

    def get_disc_containers(self):
        tracklist_table = self.parsed_response.cssselect('div#album_tabs_tracklist table.table_lyrics tbody')
        if len(tracklist_table) != 1:
            self.raise_exception(u'could not find tracklist table')
        tracklist_table = tracklist_table[0]
        table_rows = tracklist_table.cssselect('tr')
        disc_containers = {}
        disc_number = 1
        for row in table_rows:
            columns = row.cssselect('td')
            if len(columns) == 1:
                header = columns[0].text_content()
                m = re.match('(?:Disc|CD) (\d+)', header)
                if m:
                    disc_number = int(m.group(1))
            elif len(columns) == 4:
                if not disc_number in disc_containers:
                    disc_containers[disc_number] = []

                disc_containers[disc_number].append(columns)
            else:
                continue
        return disc_containers

    def get_track_number(self, track_container):
        (track_number_td, track_title_td, track_length_td, lyrics_td) = track_container
        m = re.search('(\d+)(?:\.)?', track_number_td.text_content())
        if m:
            track_number_without_zeros = m.group(1).lstrip('0')
            if track_number_without_zeros:
                track_number = track_number_without_zeros
            else:
                track_number = '0'
        else:
            self.raise_exception(u'could not extract track number')
        return track_number

    def get_track_title(self, track_container):
        (track_number_td, track_title_td, track_length_td, lyrics_td) = track_container
        track_title = self.remove_whitespace(track_title_td.text_content())
        return track_title

    def get_track_length(self, track_container):
        (track_number_td, track_title_td, track_length_td, lyrics_td) = track_container
        track_length = self.remove_whitespace(track_length_td.text_content())
        if track_length:
            i = 0
            length = 0
            for component in reversed(track_length.split(':')):
                length += int(component) * 60**i
                i += 1
            return length
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

        #stupid website doesn't send correct http status code
        h3_404 = self.parsed_response.cssselect('h3')
        for candidate in h3_404:
            if candidate.text_content() == 'Error 404':
                self.result = NotFoundResult()
                self.result.set_scraper_name(self.get_name())
                return self.result

        self.result = ReleaseResult()
        self.result.set_scraper_name(self.get_name())

        self.add_release_event()

        self.add_release_format()

        self.add_label_ids()

        self.add_release_title()

        self.add_release_artists()

        self.add_discs()

        release_url = self.get_original_string()
        if not release_url:
            release_url = self.get_full_url()
        if release_url:
            self.result.set_url(release_url)

        return self.result


class SearchScraper(SearchScraperBase, RequestMixin, ExceptionMixin, UtilityMixin):

    url = 'http://www.metal-archives.com/search/ajax-album-search/'

    forced_response_encoding = 'utf-8'

    def get_params(self):
        return {'field': 'title', 'query': self.search_term}

    def prepare_response_content(self, content):
        try:
            self.parsed_response = json.loads(content)
        except:
            self.raise_exception(u'invalid server response')

    def get_release_containers(self):
        if 'aaData' in self.parsed_response:
            return self.parsed_response['aaData'][:25]
        return []

    def get_release_name_and_url(self, release_container):
        (artists_html, title_html, type, date_html) = release_container
        artists_div = lxml.html.fragment_fromstring(artists_html, create_parent="div")
        title_div = lxml.html.fragment_fromstring(title_html, create_parent="div")

        artists_a = artists_div.cssselect('a')
        if len(artists_a) == 0:
            self.raise_exception(u'could not extract artists')

        artists = []
        for artist_a in artists_a:
            artists.append(self.remove_whitespace(artist_a.text_content()))

        title_a = title_div.cssselect('a')
        if len(title_a) != 1:
            self.raise_exception(u'could not extract release title')
        title_a = title_a[0]
        title = title_a.text_content()

        release_url = title_a.attrib['href']
        m = re.match(ReleaseScraper.string_regex, release_url)
        if not m:
            release_url = None

        return u', '.join(artists) + u' \u2013 ' + title, release_url

    def get_release_info(self, release_container):
        (artists_html, title_html, type, date_html) = release_container
        date_div = lxml.html.fragment_fromstring(date_html, create_parent="div")

        date = date_div.text_content()
        date = self.remove_whitespace(date)

        info_components = filter(lambda x: x, [date, type])

        return u' | '.join(info_components)

    def get_result(self):
        response = self.request_get(url=self.url, params=self.get_params())
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