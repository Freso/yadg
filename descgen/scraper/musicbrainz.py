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
import json
from .base import Scraper, ExceptionMixin, RequestMixin, UtilityMixin, StatusCodeError, StandardFactory
from .base import SearchScraper as SearchScraperBase
from ..result import ReleaseResult, ListResult, NotFoundResult


READABLE_NAME = 'Musicbrainz'
SCRAPER_URL = 'http://musicbrainz.org/'


class ReleaseScraper(Scraper, RequestMixin, ExceptionMixin, UtilityMixin):

    _base_url = 'http://musicbrainz.org/'
    string_regex = '^http(?:s)?://(?:www\.)?musicbrainz.org/release/([A-Za-z0-9\-]+)$'

    def __init__(self, id):
        super(ReleaseScraper, self).__init__()
        self.id = id

        self.main_release_artists = []

    def get_instance_info(self):
        return u'id="%s"' % self.id

    def get_url(self):
        return self._base_url + 'release/%s' % self.id

    def _get_dd_from_dt(self, search_term, dl_children):
        dl_children = filter(lambda x: x.tag.lower() in ('dt', 'dd'), dl_children)
        if len(dl_children) % 2 == 1:
            self.raise_exception(u'dl has uneven number of children')
        while dl_children:
            dt = dl_children[0].text_content()
            dd = dl_children[1]
            dl_children = dl_children[2:]
            if dt == search_term:
                return dd
        return None

    def _get_js_data(self):
        script_tag = filter(lambda x: 'MB.Release.init' in x.text_content(), self.parsed_response.cssselect('script'))
        if len(script_tag) != 1:
            self.raise_exception(u'could not find javascript release information')
        m = re.search('MB\.Release\.init\((.*)\)', script_tag[0].text_content())
        if not m:
            self.raise_exception(u'could not extract json object')
        try:
            self.javascript_object = json.loads(m.group(1))['mediums']
        except Exception as e:
            self.raise_exception(u'could not decode json object, error: ' + unicode(e))
        allArtistCredits = [item for sublist in map(lambda medium: map(lambda track: track['artistCredit'], medium['tracks']), self.javascript_object) for item in sublist]
        self.show_artists = False
        for artistCredit in allArtistCredits[1:]:
            if artistCredit != allArtistCredits[0]:
                self.show_artists = True
                break

    def prepare_response_content(self, content):
        #get the raw response content and parse it
        self.parsed_response = lxml.html.document_fromstring(content)

        #get the content div
        content_div = self.parsed_response.cssselect('div#content')
        if len(content_div) != 1:
            self.raise_exception(u'could not find content div')
        content_div = content_div[0]

        #prepare the contents of the sidebar
        sidebar_div = self.parsed_response.cssselect('div#sidebar')
        if len(sidebar_div) != 1:
            self.raise_exception(u'could not find sidebar div')
        sidebar_div = sidebar_div[0]

        sidebar_h2 = sidebar_div.cssselect('h2')

        self._sidebar_captions = dict(map(lambda x: (x.text_content(), x), sidebar_h2))

        releaseheader_div = content_div.cssselect('div.releaseheader')
        if len(releaseheader_div) != 1:
            self.raise_exception(u'could not find releaseheader div')
        self._release_header_div = releaseheader_div[0]

        tracklist_h2 = filter(lambda x: x.text_content() == 'Tracklist', content_div.cssselect('h2'))
        if len(tracklist_h2) == 1:
            self._tracklist_caption = tracklist_h2[0]
        else:
            self._tracklist_caption = None

        self._get_js_data()

    def add_release_event(self):
        if 'Release events' in self._sidebar_captions:
            caption = self._sidebar_captions['Release events']

            ul = caption.getnext()
            lis = ul.cssselect('li')

            for li in lis:
                date = None
                country = None
                release_event = self.result.create_release_event()
                release_date_span = li.cssselect('.release-date')
                if len(release_date_span) == 1:
                    date = self.remove_whitespace(release_date_span[0].text_content())
                    if date:
                        release_event.set_date(date)
                country_bdi = li.cssselect('a bdi')
                if len(country_bdi) == 1:
                    country = self.remove_whitespace(country_bdi[0].text_content())
                    if country:
                        release_event.set_country(country)
                if date or country:
                    self.result.append_release_event(release_event)

    def add_release_format(self):
        if 'Release information' in self._sidebar_captions:
            caption = self._sidebar_captions['Release information']

            dl = caption.getnext()
            children = dl.getchildren()
            dd_format = self._get_dd_from_dt('Format:', children)
        else:
            dd_format = None

        if 'Additional details' in self._sidebar_captions:
            caption = self._sidebar_captions['Additional details']

            dl = caption.getnext()
            children = dl.getchildren()
            dd_type = self._get_dd_from_dt('Type:', children)
        else:
            dd_type = None

        format = ''

        if dd_format is not None:
            dd_format = dd_format.text_content()
            if dd_format != '(unknown)':
                format = dd_format

        if dd_type is not None:
            if format:
                format += ', ' + self.remove_whitespace(dd_type.text_content())
            else:
                format = self.remove_whitespace(dd_type.text_content())

        if format:
            self.result.set_format(format)

    def add_label_ids(self):
        if 'Labels' in self._sidebar_captions:
            caption = self._sidebar_captions['Labels']

            label_ul = caption.getnext()
            label_li = label_ul.cssselect('li')

            for li in label_li:
                label_a = li.cssselect('a')
                if len(label_a) == 1:
                    label_a = label_a[0]
                else:
                    #if we cannot find the label we assume something is wrong
                    self.raise_exception('could not find label link in label li')

                label_name = self.remove_whitespace(label_a.text_content())
                label_id = self.result.create_label_id()
                label_id.set_label(label_name)

                cat_nr_span = li.cssselect('.catalog-number')
                if len(cat_nr_span) == 1:
                    catalog_number = self.remove_whitespace(cat_nr_span[0].text_content())
                    if catalog_number:
                        label_id.append_catalogue_nr(catalog_number)

                self.result.append_label_id(label_id)

    def add_release_title(self):
        title_a = self._release_header_div.cssselect('h1 a')
        if len(title_a) != 1:
            self.raise_exception(u'could not find release title a')
        title_a = title_a[0]
        title = self.remove_whitespace(title_a.text_content())
        if title:
            self.result.set_title(title)

    def add_release_artists(self):
        artist_links = self._release_header_div.cssselect('p.subheader a')
        artist_links = filter(lambda x: 'href' in x.attrib and '/artist/' in x.attrib['href'], artist_links)
        if len(artist_links) == 0:
            self.raise_exception(u'could not find artist a')

        for artist_a in artist_links:
            artist_name = self.remove_whitespace(artist_a.text_content())
            artist = self.result.create_artist()
            if artist_name == 'Various Artists':
                artist.set_various(True)
            else:
                artist.set_name(artist_name)
            artist.append_type(self.result.ArtistTypes.MAIN)
            self.result.append_release_artist(artist)
            self.main_release_artists.append(artist)

    def get_disc_containers(self):
        return dict(zip([i for i in range(1, len(self.javascript_object)+1)], self.javascript_object))

    def get_disc_title(self, disc_container):
        if 'name' in disc_container and disc_container['name']:
            return disc_container['name']
        return None

    def get_track_containers(self, disc_container):
        if 'tracks' in disc_container and disc_container['tracks']:
            return disc_container['tracks']
        else:
            return []

    def get_track_number(self, track_container):
        if not 'number' in track_container or not track_container['number']:
            self.raise_exception(u'could not find track number')
        return track_container['number']

    def get_track_artists(self, track_container, include_main_artists):
        track_artists = []
        is_feature = False
        if self.show_artists and 'artistCredit' in track_container and track_container['artistCredit']:
            for artistCredit in track_container['artistCredit']:
                if 'name' in artistCredit:
                    track_artist = self.remove_whitespace(artistCredit['name'])
                    artist = self.result.create_artist()
                    if track_artist == 'Various Artists':
                        artist.set_various(True)
                    else:
                        artist.set_name(track_artist)
                    if is_feature:
                        artist.append_type(self.result.ArtistTypes.FEATURING)
                    else:
                        artist.append_type(self.result.ArtistTypes.MAIN)
                    if is_feature or include_main_artists:
                        track_artists.append(artist)
                    if u'feat.' in artistCredit['joinPhrase']:
                        is_feature = True
        return track_artists

    def get_track_title(self, track_container):
        if not 'name' in track_container or not track_container['name']:
            self.raise_exception(u'could not find track title')
        return track_container['name']

    def get_track_length(self, track_container):
        if 'length' in track_container and track_container['length']:
            return int(round(track_container['length'] / float(1000)))
        return None

    def add_discs(self):
        disc_containers = self.get_disc_containers()

        # check if the release main artists are equal to all main track artists
        track_artists_equal_main_artists = True
        for disc_nr in disc_containers:
            for track_container in self.get_track_containers(disc_containers[disc_nr]):
                track_artists = self.get_track_artists(track_container, True)
                main_track_artists = filter(lambda x: self.result.ArtistTypes.MAIN in x.get_types(), track_artists)
                track_artists_equal_main_artists &= self.main_release_artists == main_track_artists
                if not track_artists_equal_main_artists:
                    break
            if not track_artists_equal_main_artists:
                break

        for disc_nr in disc_containers:
            disc = self.result.create_disc()
            disc.set_number(disc_nr)

            disc_title = self.get_disc_title(disc_containers[disc_nr])
            if disc_title:
                disc.set_title(disc_title)

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
                track_artists = self.get_track_artists(track_container, not track_artists_equal_main_artists)
                for track_artist in track_artists:
                    track.append_artist(track_artist)

                disc.append_track(track)
            self.result.append_disc(disc)

    def get_result(self):
        try:
            response = self.request_get(self.get_url())
        except StatusCodeError as e:
            # MusicBrainz throws a 400 BAD REQUEST if the ID is malformed
            # so make sure we return a NotFoundResult in that case
            if str(e) == "404" or str(e) == "400":
                self.result = NotFoundResult()
                self.result.set_scraper_name(self.get_name())
                return self.result
            else:
                self.raise_exception("request to server unsuccessful, status code: %s" % str(e))

        self.result = ReleaseResult()
        self.result.set_scraper_name(self.get_name())

        self.prepare_response_content(self.get_response_content(response))

        self.add_release_event()

        self.add_release_format()

        self.add_label_ids()

        self.add_release_title()

        self.add_release_artists()

        self.add_discs()

        release_url = self.get_original_string()
        if not release_url:
            release_url = self.get_url()
        if release_url:
            self.result.set_url(release_url)

        return self.result


class ReleaseGroupScraper(Scraper, RequestMixin, ExceptionMixin, UtilityMixin):

    _base_url = 'http://musicbrainz.org/'
    string_regex = '^http://(?:www\.)?musicbrainz.org/release-group/([A-Za-z0-9\-]+)$'

    def __init__(self, id):
        super(ReleaseGroupScraper, self).__init__()
        self.id = id

    def get_instance_info(self):
        return u'id="%s"' % self.id

    def get_url(self):
        return self._base_url + 'release-group/%s' % self.id

    def prepare_response_content(self, content):
        #get the raw response content and parse it
        self.parsed_response = lxml.html.document_fromstring(content)

    def _get_release_group_artists(self):
        artist_links = self.parsed_response.cssselect('div#content div.rgheader p.subheader a')
        artist_links = filter(lambda x: 'href' in x.attrib and '/artist/' in x.attrib['href'], artist_links)
        if len(artist_links) == 0:
            self.raise_exception(u'could not find artist a')

        artist_names = []

        for artist_a in artist_links:
            artist_name = self.remove_whitespace(artist_a.text_content())
            artist_names.append(artist_name)

        return artist_names

    def get_release_containers(self):
        result_table = self.parsed_response.cssselect('div#content table.tbl')

        if len(result_table) != 1:
            #no results
            return []
        result_table = result_table[0]

        return filter(lambda x: len(x) == 8, map(lambda x: x.getchildren(), result_table.cssselect('tbody tr')))

    def get_release_name_and_url(self, release_container):
        name = None
        artist_names = self._get_release_group_artists()
        title_col = release_container[0]
        title_a = title_col.cssselect('a')
        if len(title_a) != 1:
            self.raise_exception(u'could not determine release title')
        title_a = title_a[0]
        release_url = title_a.attrib['href']
        m = re.match(ReleaseScraper.string_regex, release_url)
        if not m:
            release_url = None
        #get release title
        title = self.remove_whitespace(title_a.text_content())

        if len(artist_names) != 0 or title:
            name = u', '.join(artist_names)
            if name:
                name += u' \u2013 '
            name += title
        return name, release_url

    def get_release_info(self, release_container):
        components = release_container[1:]
        components = filter(lambda x: x and not '(unknown)' in x, map(lambda x: self.remove_whitespace(x.text_content()), components))
        info = u' | '.join(components)
        if info:
            return info
        return None

    def get_result(self):
        try:
            response = self.request_get(self.get_url())
        except StatusCodeError as e:
            # MusicBrainz throws a 400 BAD REQUEST if the ID is malformed
            # so make sure we return a empty ListResult in that case
            if str(e) == "404" or str(e) == "400":
                self.result = ListResult()
                self.result.set_scraper_name(self.get_name())
                return self.result
            else:
                self.raise_exception("request to server unsuccessful, status code: %s" % str(e))

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


class SearchScraper(SearchScraperBase, RequestMixin, ExceptionMixin, UtilityMixin):

    url = 'http://musicbrainz.org/search'

    def get_params(self):
        return {'type': 'release', 'limit': '25', 'query': self.search_term}

    def prepare_response_content(self, content):
        #get the raw response content and parse it
        self.parsed_response = lxml.html.document_fromstring(content)

    def get_release_containers(self):
        result_table = self.parsed_response.cssselect('div#content table.tbl')

        if len(result_table) != 1:
            #no results
            return []
        result_table = result_table[0]

        return map(lambda x: x.getchildren(), result_table.cssselect('tbody tr'))

    def get_release_name_and_url(self, release_container):
        name = None
        title_col = release_container[1]
        artist_col = release_container[2]
        title_a = title_col.cssselect('a')
        if len(title_a) != 1:
            self.raise_exception(u'could not determine release title')
        title_a = title_a[0]
        release_url = title_a.attrib['href']
        m = re.match(ReleaseScraper.string_regex, release_url)
        if not m:
            release_url = None
        #get release title
        title = self.remove_whitespace(title_a.text_content())
        #get artist link
        artist_links = artist_col.cssselect('a')
        if len(artist_links) == 0:
            self.raise_exception(u'could not determine release artist')
        #get release artist
        artists = []
        for artist_a in artist_links:
            artist = self.remove_whitespace(artist_a.text_content())
            artists.append(artist)
        if len(artists) != 0 or title:
            name = u', '.join(artists)
            if name:
                name += u' \u2013 '
            name += title
        return name, release_url

    def get_release_info(self, release_container):
        format_col = release_container[3]
        track_count_col = release_container[4]
        date_col = release_container[5]
        country_col = release_container[6]
        #get format
        format = self.remove_whitespace(format_col.text_content())
        #get track count
        track_count = self.remove_whitespace(track_count_col.text_content())
        if track_count:
            track_count += u' tracks'
        #get date
        date = self.remove_whitespace(date_col.text_content())
        #get country
        country = self.remove_whitespace(country_col.text_content())
        if country:
            country = u'Country: ' + country
        info = u' | '.join(filter(lambda x: x, [format, track_count, date, country]))
        if info:
            return info
        return None

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

    scraper_classes = [ReleaseScraper, ReleaseGroupScraper]
    search_scraper = SearchScraper