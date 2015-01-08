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

import re
from .base import ExceptionMixin, RequestMixin, UtilityMixin, RateLimitMixin, StatusCodeError, StandardFactory
from .base import SearchScraper as SearchScraperBase
from .base import Scraper as ScraperBase
from ..result import ReleaseResult, ListResult, NotFoundResult
from rauth import OAuth1Service
import json
import secret


READABLE_NAME = 'Discogs'
SCRAPER_URL = 'http://www.discogs.com/'

_API_BASE_URL = 'https://api.discogs.com/'
_APP_IDENTIFIER = 'YADG/0.1'
RATE_LIMIT = '0.7/s'
CONCURRENCY = 1

CONSUMER_KEY = secret.DISCOGS_CONSUMER_KEY
CONSUMER_SECRET = secret.DISCOGS_CONSUMER_SECRET
ACCESS_TOKEN = secret.DISCOGS_ACCESS_TOKEN
ACCESS_SECRET = secret.DISCOGS_ACCESS_SECRET

discogsOauth = OAuth1Service(
    name='discogs',
    base_url=_API_BASE_URL,
    request_token_url='https://api.discogs.com/oauth/request_token',
    access_token_url='https://api.discogs.com/oauth/access_token',
    authorize_url='http://www.discogs.com/oauth/authorize',
    consumer_key=CONSUMER_KEY,
    consumer_secret=CONSUMER_SECRET
)


class Scraper(ScraperBase, UtilityMixin, RequestMixin):

    _base_url = 'http://www.discogs.com/'
    _api_base_url = _API_BASE_URL

    headers = {'User-Agent': _APP_IDENTIFIER}

    @staticmethod
    def _get_args_from_match(match):
        return (int(match.group(1)), )

    def _remove_enum_suffix(self, string):
        return re.sub(u'(.*) \(\d+\)$', r'\1', string)

    def _prepare_artist_name(self, artist_name):
        artist_name = self._remove_enum_suffix(artist_name)
        artist_name = self.swap_suffix(artist_name)
        return artist_name

    def _get_artist_name(self, artist):
        if 'anv' in artist and artist['anv']:
            artist_name = artist['anv']
        else:
            artist_name = artist['name']
        return self._prepare_artist_name(self.remove_whitespace(artist_name))


class ReleaseScraper(Scraper, ExceptionMixin):

    string_regex = '^http(?:s)?://(?:www\.)?discogs\.com/(?:.+?/)?release/(\d+)$'

    ARTIST_NAME_VARIOUS = "Various"

    _featuring_artist_regex = u'(?i)feat(uring)?\.?'

    def __init__(self, id):
        super(ReleaseScraper, self).__init__()
        self.id = id
        self.data = {}

    def get_instance_info(self):
        return u'id="%d"' % self.id

    def get_url(self):
        if 'url' in self.data:
            return self.data['url']
        else:
            return self._base_url + 'release/%d' % self.id

    def get_api_url(self):
        return self._api_base_url + 'releases/%d' % self.id

    def _split_infos(self, info_string):
        components = info_string.split(',')
        #remove leading and trailing whitespace
        components = map(lambda x: x.strip().strip(u' &').strip('& '), components)
        #remove empty elements
        components = filter(lambda x: x, components)
        return components

    def _get_main_and_feat_artists(self, artist_elements):
        artists = []
        is_feature = False
        for artist_element in artist_elements:
            artist = self.result.create_artist()
            artist_name = self._get_artist_name(artist_element)
            is_various = artist_name == self.ARTIST_NAME_VARIOUS
            if not is_various:
                artist.set_name(artist_name)
            artist.set_various(is_various)
            if is_feature:
                # we assume every artist after "feat." is a feature
                artist.append_type(self.result.ArtistTypes.FEATURING)
            else:
                artist.append_type(self.result.ArtistTypes.MAIN)
                if re.search(self._featuring_artist_regex, artist_element['join']):
                    # all artists after this one are features
                    is_feature = True
            artists.append(artist)
        return artists

    def _get_tracks(self, track_list, disc_containers):
        for track in filter(lambda x: x['type_'] in [u'track', u'index'], track_list):
            if track['type_'] == u'track':
                #determine cd and track number
                m = re.search('(?i)^(?:(?:(?:cd)?(\d{1,2})(?:-|\.|:))|(?:cd(?:\s+|\.|-)))?(\d+|(\w{1,2}\s?\d*)|(face )?[ivxc]+)(?:\.)?$', track['position'])
                if not m:
                    #ignore tracks with strange track number
                    continue
                cd_number = m.group(1)
                track_number_string = m.group(2)
                #if there is no cd number we default to 1
                if not cd_number:
                    cd_number = 1
                elif re.search('\D', track_number_string):
                    # track number like: 11-A
                    # here 11 is most likely not the cd number, but the whole thing is a weird designation for a sub track
                    # let's try to just ignore the track and see where we will come crashing down
                    continue
                else:
                    cd_number = int(cd_number)
                if not cd_number in disc_containers:
                    disc_containers[cd_number] = []
                disc_containers[cd_number].append({'track': track, 'track_number_string': track_number_string})
            elif track['type_'] == u'index' and 'sub_tracks' in track:
                self._get_tracks(track['sub_tracks'], disc_containers)

    def parse_response_content(self, response_content):
        try:
            response = json.loads(response_content)
        except:
            self.raise_exception(u'invalid server response: %r' % response_content)
        return response

    def add_release_event(self):
        release_event = self.result.create_release_event()
        found = False
        if 'released_formatted' in self.data:
            release_event.set_date(self.data['released_formatted'])
            found = True
        if 'country' in self.data:
            release_event.set_country(self.data['country'])
            found = True
        if found:
            self.result.append_release_event(release_event)

    def add_release_format(self):
        if 'formats' in self.data:
            format_strings = []
            for format in self.data['formats']:
                format_string = u''
                if 'qty' in format and format['qty'] and format['qty'] != u'1':
                    format_string = u'%s \xd7 ' % (format['qty'])
                format_string_components = []
                if 'name' in format and format['name']:
                    format_string_components.append(format['name'])
                if 'descriptions' in format:
                    format_string_components.extend(format['descriptions'])
                if 'text' in format and format['text']:
                    format_string_components.append(format['text'])
                format_string += u', '.join(format_string_components)
                format_strings.append(format_string)
            self.result.set_format(u', '.join(format_strings))

    def add_label_ids(self):
        if 'labels' in self.data:
            for label in self.data['labels']:
                if 'name' in label:
                    label_id = self.result.create_label_id()
                    label_id.set_label(self._remove_enum_suffix(label['name']))
                    if 'catno' in label and label['catno'] != 'none':
                        label_id.append_catalogue_nr(label['catno'])
                    self.result.append_label_id(label_id)

    def add_release_title(self):
        if 'title' in self.data:
            self.result.set_title(self.remove_whitespace(self.data['title']))

    def add_release_artists(self):
        if 'artists' in self.data:
            for artist in self._get_main_and_feat_artists(self.data['artists']):
                self.result.append_release_artist(artist)

    def add_genres(self):
        if 'genres' in self.data:
            for genre in [item for sublist in map(self._split_infos, self.data['genres']) for item in sublist]:
                self.result.append_genre(genre)

    def add_styles(self):
        if 'styles' in self.data:
            for style in [item for sublist in map(self._split_infos, self.data['styles']) for item in sublist]:
                self.result.append_style(style)

    def get_disc_containers(self):
        disc_containers = {}
        if 'tracklist' in self.data:
            self._get_tracks(self.data['tracklist'], disc_containers)
        return disc_containers

    def get_track_number(self, trackContainer):
        number = trackContainer['track_number_string']
        if not re.search('\D', number):
            #remove leading zeros
            number_without_zeros = number.lstrip('0')
            #see if there is anything left
            if number_without_zeros:
                number = number_without_zeros
            else:
                #number consists only of zeros
                number = '0'
        if number:
            return number
        return None

    def get_track_artists(self, trackContainer):
        track_artists = []
        track_artist_names = {}
        if 'artists' in trackContainer['track']:
            for track_artist in self._get_main_and_feat_artists(trackContainer['track']['artists']):
                track_artists.append(track_artist)
                track_artist_names[track_artist.get_name()] = track_artist
        #there might be featuring artists in extraArtists
        if 'extraartists' in trackContainer['track']:
            for extra_artist in trackContainer['track']['extraartists']:
                role = extra_artist['role']
                if re.match(u'(?s).*(Featuring|Remix).*', role):
                    if u'Featuring' in role:
                        track_artist_type = self.result.ArtistTypes.FEATURING
                    elif u'Remix' in role:
                        track_artist_type = self.result.ArtistTypes.REMIXER
                    track_artist_name = self._get_artist_name(extra_artist)
                    if not track_artist_name in track_artist_names:
                        # only add the additional artist if we didn't already add an artist with the same name
                        track_artist = self.result.create_artist()
                        track_artist.set_name(track_artist_name)
                        track_artist.append_type(track_artist_type)
                        track_artists.append(track_artist)
                        track_artist_names[track_artist_name] = track_artist
                    elif not track_artist_type in track_artist_names[track_artist_name].get_types():
                        # otherwise add the new type to the existing track artist
                        track_artist_names[track_artist_name].append_type(track_artist_type)
        return track_artists

    def get_track_title(self, trackContainer):
        if trackContainer['track']['title']:
            return self.remove_whitespace(trackContainer['track']['title'])
        return None

    def get_track_length(self, trackContainer):
        if trackContainer['track']['duration']:
            return self.seconds_from_string(trackContainer['track']['duration'])
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
            response = self.request_get(url=self.get_api_url())
        except StatusCodeError as e:
            if str(e) == "404":
                self.result = NotFoundResult()
                self.result.set_scraper_name(self.get_name())
                return self.result
            else:
                raise e

        self.data = self.parse_response_content(self.get_response_content(response))

        self.result = ReleaseResult()
        self.result.set_scraper_name(self.get_name())

        self.add_release_event()

        self.add_release_format()

        self.add_label_ids()

        self.add_release_title()

        self.add_release_artists()

        self.add_genres()

        self.add_styles()

        self.add_discs()

        release_url = self.get_original_string()
        if not release_url:
            release_url = self.get_url()
        if release_url:
            self.result.set_url(release_url)

        return self.result


class MasterScraper(Scraper, ExceptionMixin, RateLimitMixin):

    string_regex = '^http(?:s)?://(?:www\.)?discogs\.com/(?:.+?/)?master/(\d+)$'

    rate_limit = RATE_LIMIT

    def __init__(self, id):
        super(MasterScraper, self).__init__()
        self.id = id
        self.data_master = {}
        self.data_versions = {}

    def get_instance_info(self):
        return u'id="%d"' % self.id

    def parse_response_content(self, response_content):
        try:
            response = json.loads(response_content)
        except:
            self.raise_exception(u'invalid server response: %r' % response_content)
        return response

    def get_artist_string(self):
        artist_names = []
        if 'artists' in self.data_master:
            for artist in self.data_master['artists']:
                artist_name = self._get_artist_name(artist)
                artist_names.append(artist_name)
                if 'join' in artist and artist['join']:
                    artist_names.append(self.remove_whitespace(artist['join']))
        return u' '.join(artist_names)

    def get_release_containers(self):
        if 'versions' in self.data_versions:
            return self.data_versions['versions']
        return []

    def get_release_name_and_url(self, release_container):
        release_name = None
        if 'title' in release_container:
            release_name = self.remove_whitespace(release_container['title'])
        release_url = None
        if 'id' in release_container:
            release_url = self._base_url + u'release/%d' % release_container['id']
        return release_name, release_url

    def get_release_info(self, release_container):
        #get additional info
        components = []
        for key in ['format', 'label', 'catno', 'country', 'released']:
            if key in release_container:
                value = self.remove_whitespace(release_container[key])
                if value:
                    components.append(value)
        if components:
            return u' | '.join(components)
        return None

    def get_result(self):
        try:
            self.rate_limit_sleep()
            response_master = self.request_get(url=self._api_base_url + 'masters/%d' % self.id)
            self.rate_limit_sleep()
            response_versions = self.request_get(url=self._api_base_url + 'masters/%d/versions' % self.id)
        except StatusCodeError as e:
            if str(e) == "404":
                self.result = NotFoundResult()
                self.result.set_scraper_name(self.get_name())
                return self.result
            else:
                raise e

        self.data_master = self.parse_response_content(self.get_response_content(response_master))
        self.data_versions = self.parse_response_content(self.get_response_content(response_versions))

        result = ListResult()
        result.set_scraper_name(self.get_name())

        release_artist = self.get_artist_string()
        release_containers = self.get_release_containers()
        for release_container in release_containers:
            release_name, release_url = self.get_release_name_and_url(release_container)

            # we only add releases to the result list that we can actually access
            if release_url is not None and release_name is not None:
                release_info = self.get_release_info(release_container)

                list_item = result.create_item()
                list_item.set_name(release_artist + u' – ' + release_name)
                list_item.set_info(release_info)
                list_item.set_query(release_url)
                list_item.set_url(release_url)
                result.append_item(list_item)
        return result


class SearchScraper(SearchScraperBase, RequestMixin, ExceptionMixin, UtilityMixin):

    discogsOauth=discogsOauth

    url = _API_BASE_URL + 'database/search'

    data = {}

    def get_new_session(self):
        return self.discogsOauth.get_session((ACCESS_TOKEN, ACCESS_SECRET))

    def get_params(self):
        return {'type': 'release', 'per_page': '20', 'q': self.search_term}

    def parse_response_content(self, response_content):
        try:
            response = json.loads(response_content)
        except:
            self.raise_exception(u'invalid server response: %r' % response_content)
        return response

    def get_release_containers(self):
        if 'results' in self.data:
            return self.data['results']
        return []

    def get_release_name_and_url(self, release_container):
        release_name = None
        if 'title' in release_container:
            release_name = self.remove_whitespace(release_container['title'])
        release_url= None
        if 'uri' in release_container:
            uri = release_container['uri']
            # make the release URL a fully qualified one
            if uri.startswith('/'):
                release_url = 'http://www.discogs.com' + uri
        return release_name, release_url

    def get_release_info(self, release_container):
        #get additional info
        components = []
        if 'format' in release_container:
            format = u', '.join(release_container['format'])
            if format:
                components.append(format)
        if 'label' in release_container and len(release_container['label']) > 0:
            # there can be a whole lot of labels in the list, so just take the first one
            components.append(release_container['label'][0])
        # additional components that don't require special handling
        for key in ['catno', 'country', 'year']:
            if key in release_container:
                value = self.remove_whitespace(release_container[key])
                if value:
                    components.append(value)
        if components:
            return u' | '.join(components)
        return None

    def get_result(self):
        response = self.request_get(url=self.url, params=self.get_params())
        self.data = self.parse_response_content(self.get_response_content(response))

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

    scraper_classes = (MasterScraper, ReleaseScraper)
    search_scraper = SearchScraper

    global_rate_limit = RATE_LIMIT
    global_concurrency = CONCURRENCY