#!/usr/bin/python
# -*- coding: utf-8 -*-

import lxml.html
import re
from .base import Scraper, ExceptionMixin, RequestMixin, UtilityMixin, StatusCodeError, StandardFactory
from .base import SearchScraper as SearchScraperBase
from ..result import ReleaseResult, ListResult, NotFoundResult


READABLE_NAME = 'Musik-Sammler'
SCRAPER_URL = 'http://www.musik-sammler.de/'
NOTES = '*  Search terms are only matched against **album titles**\n' \
        '*  Release country names in description are in German'


class ReleaseScraper(Scraper, RequestMixin, ExceptionMixin, UtilityMixin):

    _base_url = 'http://www.musik-sammler.de/'
    string_regex = '^http://(?:www\.)?musik-sammler\.de/media/(\d*?)/?$'

    _VARIOUS_ARTISTS_NAME = 'diverse interpreten'

    def __init__(self, id):
        super(ReleaseScraper, self).__init__()
        self.id = id

        self._info_dict = None

    def get_instance_info(self):
        return u'id=%s' % self.id

    def get_url(self):
        return self._base_url + 'media/%s' % self.id

    def _get_info_dict(self):
        if self._info_dict is None:
            self._info_dict = {}
            info_table_rows = self.parsed_response.cssselect('div#mdata table#mediaCoreData tr')
            for info_row in info_table_rows:
                children = info_row.getchildren()
                if len(children) == 2:
                    th, td = children
                    content = td.text_content().lower()
                    if not ('unbekannt' in content or 'k.a.' in content):
                        self._info_dict[self.remove_whitespace(th.text_content()).lower()] = td
        return self._info_dict

    def prepare_response_content(self, content):
        #get the raw response content and parse it
        self.parsed_response = lxml.html.document_fromstring(content)

    def add_release_event(self):
        info_dict = self._get_info_dict()
        release_event = self.result.create_release_event()
        date = None
        if 'jahr' in info_dict:
            date = self.remove_whitespace(info_dict['jahr'].text_content())
        elif 'orig. release' in info_dict:
            date = self.remove_whitespace(info_dict['orig. release'].text_content())
        if date:
            release_event.set_date(date)
        country = None
        if 'herstellungsland' in info_dict:
            img = info_dict['herstellungsland'].cssselect('img')
            if len(img) == 1:
                country = self.remove_whitespace(img[0].attrib['title'])
                release_event.set_country(country)
        if date or country:
            self.result.append_release_event(release_event)

    def add_release_format(self):
        info_dict = self._get_info_dict()
        components = []
        for key_name in (u'tonträger', 'besonderheiten'):
            if key_name in info_dict:
                components.append(self.remove_whitespace(info_dict[key_name].text_content()))
        if components:
            self.result.set_format(u', '.join(components))

    def add_label_ids(self):
        info_dict = self._get_info_dict()
        label_id = self.result.create_label_id()
        label = None
        if 'plattenfirma' in info_dict:
            label = self.remove_whitespace(info_dict['plattenfirma'].text_content())
            label_id.set_label(label)
        catalogue_nr = None
        if 'katalog-nr.' in info_dict:
            catalogue_nr = self.remove_whitespace(info_dict['katalog-nr.'].text_content())
            label_id.append_catalogue_nr(catalogue_nr)
        if label or catalogue_nr:
            self.result.append_label_id(label_id)

    def add_release_title(self):
        title_h2 = self.parsed_response.cssselect('div#minfo h2[itemprop="name"]')
        if len(title_h2) != 1:
            self.raise_exception(u'could not find album title h1')
        title_h2 = title_h2[0]
        title = self.remove_whitespace(title_h2.text_content())
        if title:
            self.result.set_title(title)

    def add_release_artists(self):
        artists_spans = self.parsed_response.cssselect('div#minfo h1[itemprop="byArtist"] span[itemprop="name"]')
        if len(artists_spans) == 0:
            self.raise_exception(u'could not find artist h2')
        for artist_span in artists_spans:
            artist_names = map(self.remove_whitespace, artist_span.text_content().split(' / '))
            for artist_name in artist_names:
                artist = self.result.create_artist()
                if artist_name.lower() == self._VARIOUS_ARTISTS_NAME:
                    artist.set_various(True)
                else:
                    artist.set_name(artist_name)
                artist.append_type(self.result.ArtistTypes.MAIN)
                # only add 'Various Artists' if it is the only artist
                if (artist.is_various() and len(artist_names) == 1 and len(artists_spans) == 1) or not artist.is_various():
                    self.result.append_release_artist(artist)

    def add_genres(self):
        info_dict = self._get_info_dict()
        if 'musikrichtung' in info_dict:
            genre_string = info_dict['musikrichtung'].text_content()
            genres = re.split(',\s+|/|:', genre_string)
            for genre_string in genres:
                genre = self.remove_whitespace(genre_string)
                if genre:
                    self.result.append_genre(genre)

    def get_disc_containers(self):
        disc_containers = {}
        tracklists = self.parsed_response.cssselect('div#tlist > table')
        disc_number = 1
        for tracklist in tracklists:
            disc_containers[disc_number] = tracklist
            disc_number += 1
        return disc_containers

    def get_track_containers(self, disc_container):
        return disc_container.cssselect('tr[itemprop="track"]')

    def get_track_number(self, track_container):
        children = track_container.getchildren()
        track_number_td = children[0]
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
        children = track_container.getchildren()
        if len(children) == 4:
            track_title_td = children[1]
        elif len(children) == 5:
            track_title_td = children[2]
        else:
            self.raise_exception(u'not the right amount of children in track container: %s' % track_container.text_content())
        track_title = self.remove_whitespace(track_title_td.text_content())
        return track_title

    def get_track_length(self, track_container):
        children = track_container.getchildren()
        if len(children) == 4:
            track_length_td = children[2]
        elif len(children) == 5:
            track_length_td = children[3]
        else:
            self.raise_exception(u'not the right amount of children in track container: %s' % track_container.text_content())
        track_length = self.remove_whitespace(track_length_td.text_content())
        if track_length:
            return self.seconds_from_string(track_length)
        return None

    def get_track_artists(self, track_container):
        children = track_container.getchildren()
        track_artists = []
        if len(children) == 5:
            track_artists_td = children[1]
            artist_as = track_artists_td.cssselect('a')
            artist_as = filter(lambda x: '/artist/' in x.attrib['href'], artist_as)
            for artist_a in artist_as:
                track_artist = self.result.create_artist()
                artist_name = self.remove_whitespace(artist_a.text_content())
                if artist_name.lower() == self._VARIOUS_ARTISTS_NAME:
                    track_artist.set_various(True)
                else:
                    track_artist.set_name(artist_name)
                track_artist.append_type(self.result.ArtistTypes.MAIN)
                # only add various artist if it is the only track artist
                if (track_artist.is_various() and len(artist_as) == 1) or not track_artist.is_various():
                    track_artists.append(track_artist)
        return track_artists

    def add_discs(self):
        disc_containers = self.get_disc_containers()
        for disc_nr in disc_containers:
            disc = self.result.create_disc()
            disc.set_number(disc_nr)

            for track_container in self.get_track_containers(disc_containers[disc_nr]):
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
            if str(e) == "404" or str(e) == "410":
                self.result = NotFoundResult()
                self.result.set_scraper_name(self.get_name())
                return self.result
            else:
                self.raise_exception("request to server unsuccessful, status code: %s" % str(e))

        self.prepare_response_content(self.get_response_content(response))

        self.result = ReleaseResult()
        self.result.set_scraper_name(self.get_name())

        self.add_release_event()

        self.add_release_format()

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


