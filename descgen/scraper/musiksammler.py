#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2011-2015 Slack
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import lxml.html
import re
from .base import Scraper, ExceptionMixin, RequestMixin, UtilityMixin, StatusCodeError, StandardFactory
from .base import SearchScraper as SearchScraperBase
from ..result import ReleaseResult, ListResult, NotFoundResult


READABLE_NAME = 'Musik-Sammler'
SCRAPER_URL = 'http://www.musik-sammler.de/'
NOTES = '*  Search terms are only matched against **album titles**\n' \
        '*  Release country names are in German\n' \
        '*  Splitting of combined artist names will not always be correct'


class ReleaseScraper(Scraper, RequestMixin, ExceptionMixin, UtilityMixin):

    _base_url = 'http://www.musik-sammler.de/'
    string_regex = '^http(?:s)?://(?:www\.)?musik-sammler\.de/media/(\d*?)/?$'

    _VARIOUS_ARTISTS_NAMES = ('diverse interpreten', 'v.a.', 'various artists/sampler')
    _UNKNOWN_SYNONYMS = ('unbekannt', 'k.a.', 'nicht vorhanden')
    _ADDITIONAL_SUFFIXES = [(u'Die ', u', Die'), (u'Der ', u', Der'), (u'Das ', u', Das')]

    def __init__(self, id):
        super(ReleaseScraper, self).__init__()
        self.id = id

        self._info_dict = None

    def get_instance_info(self):
        return u'id=%s' % self.id

    def get_url(self):
        return self._base_url + 'media/%s' % self.id

    def get_presuffixes(self):
        return self.presuffixes + self._ADDITIONAL_SUFFIXES

    def _get_info_dict(self):
        if self._info_dict is None:
            self._info_dict = {}
            info_table_rows = self.parsed_response.cssselect('div#mdata table#mediaCoreData tr')
            for info_row in info_table_rows:
                children = info_row.getchildren()
                if len(children) == 2:
                    th, td = children
                    content = self.remove_whitespace(td.text_content()).lower()
                    if not content in self._UNKNOWN_SYNONYMS:
                        self._info_dict[self.remove_whitespace(th.text_content()).lower()] = td
        return self._info_dict

    def split_artists(self, artist_string):
        artist_string = re.sub('(?i)(' + '|'.join(map(lambda x: x.replace('.', '\.'), self._VARIOUS_ARTISTS_NAMES)) + ')', 'Various Artists', artist_string)
        tokens = re.split('(?i)\s*(/|feat\.)\s*', artist_string)
        artists = []
        is_feature = False
        for token in tokens:
            if token == '/':
                continue
            elif token.lower() == 'feat.':
                is_feature = True
            elif not token:
                continue
            elif is_feature:
                artists.append({'name': token, 'is_feature': True})
            elif not is_feature:
                artists.append({'name': token, 'is_feature': False})
        return artists

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
            parsed_artists = self.split_artists(self.remove_whitespace(artist_span.text_content()))
            for parsed_artist in parsed_artists:
                artist = self.result.create_artist()
                if parsed_artist['name'] == "Various Artists":
                    artist.set_various(True)
                else:
                    artist.set_name(self.swap_suffix(parsed_artist['name']))
                if parsed_artist['is_feature']:
                    artist.append_type(self.result.ArtistTypes.FEATURING)
                else:
                    artist.append_type(self.result.ArtistTypes.MAIN)
                # only add 'Various Artists' if it is the only main artist
                if (artist.is_various() and self.result.ArtistTypes.MAIN in artist.get_types() and
                            len(filter(lambda x: not x['is_feature'], parsed_artists)) == 1 and
                            len(artists_spans) == 1) or not artist.is_various():
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
                parsed_artists = self.split_artists(self.remove_whitespace(artist_a.text_content()))
                for parsed_artist in parsed_artists:
                    track_artist = self.result.create_artist()
                    if parsed_artist['name'] == "Various Artists":
                        track_artist.set_various(True)
                    else:
                        track_artist.set_name(self.swap_suffix(parsed_artist['name']))
                    if parsed_artist['is_feature']:
                        track_artist.append_type(self.result.ArtistTypes.FEATURING)
                    else:
                        track_artist.append_type(self.result.ArtistTypes.MAIN)
                    # only add various artist if it is the only main track artist
                    if (track_artist.is_various() and len(artist_as) == 1 and
                                len(filter(lambda x: not x['is_feature'], parsed_artists)) == 1) \
                        or not track_artist.is_various():
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


class SearchScraper(SearchScraperBase, RequestMixin, ExceptionMixin, UtilityMixin):

    url = 'http://www.musik-sammler.de'

    def get_params(self):
        return {'do': 'search', 'title': self.search_term}

    def get_presuffixes(self):
        return self.presuffixes + ReleaseScraper._ADDITIONAL_SUFFIXES

    def prepare_response_content(self, content):
        #get the raw response content and parse it
        self.parsed_response = lxml.html.document_fromstring(content)

    def get_release_containers(self):
        table_rows = self.parsed_response.cssselect('table#searchArtistList tbody tr')[:25]
        return map(lambda x: x.getchildren(), table_rows)

    def get_release_name(self, release_container):
        components = []
        artist_th = release_container[2]
        artist_name = self.remove_whitespace(artist_th.text_content())
        artist_name = re.sub('(?i)(' + '|'.join(map(lambda x: x.replace('.', '\.'), ReleaseScraper._VARIOUS_ARTISTS_NAMES)) + ')', 'Various Artists', artist_name)
        album_title_th = release_container[1]
        album_title_a = album_title_th.cssselect('a')
        if len(album_title_a) != 1:
            self.raise_exception(u'could not find release link anchor')
        album_title = self.remove_whitespace(album_title_a[0].text_content())
        for c in (artist_name, album_title):
            if not c.lower() in ReleaseScraper._UNKNOWN_SYNONYMS:
                components.append(self.swap_suffix(c))
        if components:
            return u' \u2013 '.join(components)
        self.raise_exception(u'could not determine release name')

    def get_release_info(self, release_container):
        components = []
        format = release_container[3]
        year = release_container[4]
        country = release_container[5]
        catalogue_nr = release_container[7]
        for c in (format, catalogue_nr, year, country):
            c = self.remove_whitespace(c.text_content())
            if not c.lower() in ReleaseScraper._UNKNOWN_SYNONYMS:
                components.append(c)
        if components:
            return u' | '.join(components)
        return None

    def get_release_url(self, release_container):
        album_title_th = release_container[1]
        release_anchor = album_title_th.cssselect('a')
        if len(release_anchor) != 1:
            self.raise_exception(u'could not find release link anchor')
        release_link = self.url + release_anchor[0].attrib['href']
        m = re.match(ReleaseScraper.string_regex, release_link)
        if not m:
            release_link = None
        return release_link

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