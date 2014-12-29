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

import json
from .base import Scraper, ExceptionMixin, RequestMixin, UtilityMixin, StandardFactory, StatusCodeError
from .base import SearchScraper as SearchScraperBase
from ..result import ReleaseResult, ListResult, NotFoundResult

READABLE_NAME = 'Beatport'
SCRAPER_URL = 'http://www.beatport.com/'


class ReleaseScraper(Scraper, RequestMixin, ExceptionMixin, UtilityMixin):
    url = 'http://api.beatport.com/catalog/releases/detail'
    string_regex = '^http://(?:www\.)?beatport\.com/release/(.*?)/(\d+)$'

    def __init__(self, id, release_name=''):
        super(ReleaseScraper, self).__init__()
        self.id = id

        self._release_name = release_name

    def get_instance_info(self):
        return u'id=%d release_name="%s"' % (self.id, self._release_name)

    @staticmethod
    def _get_args_from_match(match):
        if not match.group(1):
            return int(match.group(2)),
        return int(match.group(2)), match.group(1)

    def get_params(self):
        return {'format': 'json', 'v': '1.0', 'id': self.id}

    def get_url(self):
        return 'http://www.beatport.com/release/%s/%d' % (self._release_name, self.id)

    def prepare_response_content(self, content):
        try:
            self.parsed_response = json.loads(content)
        except:
            self.raise_exception(u'invalid server response')

    def add_release_event(self):
        if 'releaseDate' in self.parsed_response:
            release_event = self.result.create_release_event()
            release_event.set_date(self.parsed_response['releaseDate'])
            self.result.append_release_event(release_event)

    def add_release_format(self):
        if 'category' in self.parsed_response and not self.parsed_response['category'] in ('Release', 'Uncategorized'):
            self.result.set_format(self.parsed_response['category'])

    def add_label_ids(self):
        if 'label' in self.parsed_response:
            label_id = self.result.create_label_id()
            label_id.set_label(self.parsed_response['label']['name'])
            if 'catalogNumber' in self.parsed_response:
                label_id.append_catalogue_nr(self.parsed_response['catalogNumber'])
            self.result.append_label_id(label_id)

    def add_release_title(self):
        if 'name' in self.parsed_response:
            self.result.set_title(self.parsed_response['name'])

    def add_release_artists(self):
        if 'artists' in self.parsed_response:
            #get all real 'Artists' (not 'Remixers', etc.)
            real_artists = []
            for artist in self.parsed_response['artists']:
                if artist['type'].lower() == 'artist' and artist['name']:
                    real_artists.append(artist['name'])
            # we assume that it is a Various Artists release if the release type is 'Album'
            # and the number of 'Artists' (not 'Remixers') is greater 1
            if 'category' in self.parsed_response and self.parsed_response['category'] == 'Album' and len(real_artists) > 1:
                artist = self.result.create_artist()
                artist.set_various(True)
                artist.append_type(self.result.ArtistTypes.MAIN)
                self.result.append_release_artist(artist)
            else:
                for artist_name in real_artists:
                    artist = self.result.create_artist()
                    artist.set_name(artist_name)
                    artist.append_type(self.result.ArtistTypes.MAIN)
                    self.result.append_release_artist(artist)

    def add_genres(self):
        if 'genres' in self.parsed_response:
            for genre in self.parsed_response['genres']:
                self.result.append_genre(genre['name'])

    def get_track_artists(self, track_container):
        if 'artists' in track_container:
            track_main_artists = []
            track_additional_artists = []
            for track_artist_candidate in track_container['artists']:
                if track_artist_candidate['name']:
                    artist = self.result.create_artist()
                    if track_artist_candidate['name'] == 'Various Artists':
                        artist.set_various(True)
                    else:
                        artist.set_name(track_artist_candidate['name'])
                    track_artist_type = track_artist_candidate['type'].lower()
                    if track_artist_type == 'artist':
                        artist.append_type(self.result.ArtistTypes.MAIN)
                        track_main_artists.append(artist)
                    elif track_artist_type == 'remixer':
                        artist.append_type(self.result.ArtistTypes.REMIXER)
                        track_additional_artists.append(artist)
            if track_main_artists == self.result.get_release_artists():
                track_artists = track_additional_artists
            else:
                track_artists = track_main_artists + track_additional_artists
            return track_artists
        return []

    def get_track_title(self, track_container):
        if 'name' in track_container:
            track_title = track_container['name']
            if 'mixName' in track_container and track_container['mixName'] != 'Original Mix':
                track_title += u' [' + self.remove_whitespace(track_container['mixName']) + u']'
            return track_title
        return None

    def get_track_length(self, track_container):
        if 'length' in track_container and self.remove_whitespace(track_container['length']):
            track_duration = track_container['length']
            return self.seconds_from_string(track_duration)
        return None

    def add_discs(self):
        if 'tracks' in self.parsed_response:
            disc = self.result.create_disc()
            disc.set_number(1)

            track_number = 1
            for track_container in self.parsed_response['tracks']:
                track = disc.create_track()
                track.set_number(str(track_number))
                track_title = self.get_track_title(track_container)
                if track_title:
                    track.set_title(track_title)
                track_length = self.get_track_length(track_container)
                if track_length:
                    track.set_length(track_length)
                track_artists = self.get_track_artists(track_container)
                for track_artist in track_artists:
                    track.append_artist(track_artist)
                track_number += 1
                disc.append_track(track)
            self.result.append_disc(disc)

    def get_result(self):
        try:
            response = self.request_get(url=self.url, params=self.get_params())
        except StatusCodeError as e:
            if str(e) == "404":
                result = NotFoundResult()
                result.set_scraper_name(self.get_name())
                return result
            else:
                raise e

        self.prepare_response_content(self.get_response_content(response))

        if self.parsed_response['metadata']['count'] > 1:
            self.raise_exception(u'got more than one release for given id')
        elif self.parsed_response['metadata']['count'] == 0:
            # not release with the given id was found
            # this case should be covered by the 404 error code handling above, but we just want to make sure
            result = NotFoundResult()
            result.set_scraper_name(self.get_name())
            return result

        self.parsed_response = self.parsed_response['results']

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


class SearchScraper(SearchScraperBase, RequestMixin, ExceptionMixin):
    url = 'http://api.beatport.com/catalog/search'

    def get_params(self):
        return {'v': '2.0', 'format': 'json', 'perPage': '25', 'page': '1', 'facets': ['fieldType:release', ],
                'highlight': 'false', 'query': self.search_term}

    def prepare_response_content(self, content):
        try:
            self.parsed_response = json.loads(content)
        except:
            self.raise_exception(u'invalid server response')

    def get_release_containers(self):
        if 'results' in self.parsed_response:
            return filter(lambda x: 'id' in x, self.parsed_response['results'])
        return []

    def get_release_name(self, release_container):
        name_components = []
        if 'artists' in release_container:
            #get all real 'Artists' (not 'Remixers', etc.)
            real_artists = []
            for artist in release_container['artists']:
                if artist['type'].lower() == 'artist' and artist['name']:
                    real_artists.append(artist['name'])
            # we assume that it is a Various Artists release if the release type is 'Album'
            # and the number of 'Artists' (not 'Remixers') is greater 1
            if release_container.has_key('category') and release_container['category'] == 'Album' and len(real_artists) > 1:
                artists = ['Various Artists', ]
            else:
                artists = real_artists
            if artists:
                name_components.append(u', '.join(artists))
        if 'name' in release_container:
            name_components.append(release_container['name'])
        name = u' \u2013 '.join(name_components) if name_components else None
        return name

    def get_release_info(self, release_container):
        add_info = []
        if 'releaseDate' in release_container:
            add_info.append(release_container['releaseDate'])
        if 'label' in release_container:
            add_info.append(release_container['label']['name'])
        if 'catalogNumber' in release_container:
            add_info.append(release_container['catalogNumber'])
        info = u' | '.join(add_info)
        return info

    def get_release_url(self, release_container):
        if 'id' in release_container:
            id = release_container['id']
            if 'slug' in release_container:
                slug = release_container['slug']
            else:
                slug = ''
            return 'http://www.beatport.com/release/%s/%d' % (slug, id)
        return None

    def get_result(self):
        # we don't care to catch any StatusCode exceptions here, if the status code of the api call is not equal to 200
        # then something is wrong with the api
        response = self.request_get(url=self.url, params=self.get_params())
        self.prepare_response_content(self.get_response_content(response))

        result = ListResult()
        result.set_scraper_name(self.get_name())

        release_containers = self.get_release_containers()
        for release_container in release_containers:
            release_name  = self.get_release_name(release_container)
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