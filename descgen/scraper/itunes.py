# coding=utf-8
import lxml.html, re, json
from base import BaseRelease, BaseSearch, BaseAPIError


READABLE_NAME = 'iTunes Store'


class iTunesAPIError(BaseAPIError):
    pass


class Release(BaseRelease):

    _base_url = 'http://itunes.apple.com/%s/album/'
    url_regex = '^http(?:s)?://itunes\.apple\.com/(\w{2,4})/album/([^/]*)/([^\?]+)[^/]*$'
    exception = iTunesAPIError

    exclude_genres = ['music',]

    def __init__(self, store, release_name, id):
        self.id = id
        self.store = store
        self._release_name = release_name

    def __unicode__(self):
        return u'<iTunesRelease: id=%s, store=%s>' % (self.id, self.store)

    def get_url(self):
        return self._base_url % self.store + '/' + self.id

    def get_release_url(self):
        return self._base_url % self.store + self._release_name + '/' + self.id + '?ign-mpt=uo%3D4'

    def get_params(self):
        return {'ign-mpt':'uo%3D4'}

    def _split_artists(self, artist_string):
        artists = re.split('(?:,\s?)|&', artist_string)
        artists = map(self.remove_whitespace, artists)
        return artists

    def prepare_response_content(self, content):
        #get the raw response content and parse it
        self.parsed_response = lxml.html.document_fromstring(content)

        #if the release does not exist, the website wants to connect to iTunes
        warning_div = self.parsed_response.cssselect('div.loadingbox')
        if len(warning_div) == 1:
            self.raise_exception(u'404')

        #we have to check if the track artist of each track equals the release artist
        artist_h2 = self.parsed_response.cssselect('div#title h2')
        track_artist_tds = self.parsed_response.cssselect('table.tracklist-table tbody tr.song.music td.artist')
        self._release_artist_equal_track_artists = True
        if len(artist_h2) == 1:
            release_artist = artist_h2[0].text_content()
            release_artist = self.remove_whitespace(release_artist)
            for track_artist_td in track_artist_tds:
                self._release_artist_equal_track_artists = release_artist == self.remove_whitespace(track_artist_td.text_content())
                if not self._release_artist_equal_track_artists:
                    break

    def get_release_date(self):
        release_date_span = self.parsed_response.cssselect('div#left-stack li.release-date span.label')
        if len(release_date_span) != 1:
            self.raise_exception(u'could not find release data span')
        release_date = release_date_span[0].tail
        release_date = self.remove_whitespace(release_date)
        if release_date:
            return release_date
        return None

    def get_release_title(self):
        title_h1 = self.parsed_response.cssselect('div#title h1')
        if len(title_h1) != 1:
            self.raise_exception(u'could not find release title h1')
        title = title_h1[0].text_content()
        title = self.remove_whitespace(title)
        if title:
            return title
        return None

    def get_release_artists(self):
        artists = []
        artist_h2 = self.parsed_response.cssselect('div#title h2')
        if len(artist_h2) != 1:
            self.raise_exception(u'could not find artist h2')
        artist_h2 = artist_h2[0]
        if artist_h2.text_content() == 'Various Artists':
            artists.append(self.format_artist(self.ARTIST_NAME_VARIOUS, self.ARTIST_TYPE_MAIN))
        else:
            artist_anchors = artist_h2.cssselect('a')
            for anchor in artist_anchors:
                artist_string = anchor.text_content()
                artist_strings = self._split_artists(artist_string)
                for artist in artist_strings:
                    artists.append(self.format_artist(artist, self.ARTIST_TYPE_MAIN))
        return artists

    def get_genres(self):
        genres = []
        genre_anchors = self.parsed_response.cssselect('div#left-stack li.genre a')
        for genre_anchor in genre_anchors:
            genre = genre_anchor.text_content()
            genre = self.remove_whitespace(genre)
            if not genre.lower() in self.exclude_genres:
                genres.append(genre)
        return genres

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
            if not discs.has_key(disc_num):
                discs[disc_num] = []
            discs[disc_num].append(tracklist_tr)
        return discs

    def get_track_containers(self, discContainer):
        return discContainer

    def get_track_number(self, trackContainer):
        track_num_span = trackContainer.cssselect('td.index span.index span')
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
                    for artist in artist_strings:
                        track_artists.append(self.format_artist(artist, self.ARTIST_TYPE_MAIN))
                else:
                    track_artists.append(self.format_artist(artist_string, self.ARTIST_TYPE_MAIN))
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
            return track_length
        return None


class Search(BaseSearch):

    url='http://itunes.apple.com/search'
    exception = iTunesAPIError

    def __unicode__(self):
        return u'<iTunesSearch: term="' + self.search_term + u'">'

    def get_params(self):
        return {'media':'music', 'entity':'album', 'limit':'25', 'term':self.search_term}

    def prepare_response_content(self, content):
        try:
            self.parsed_response = json.loads(content)
        except:
            self.raise_exception(u'invalid server response')

    def get_release_containers(self):
        if self.parsed_response.has_key('results'):
            return self.parsed_response['results']
        return []

    def get_release_name(self,releaseContainer):
        components = []
        for key in ['artistName', 'collectionName']:
            if releaseContainer.has_key(key):
                components.append(releaseContainer[key])
        name = u' \u2013 '.join(components)
        return name

    def get_release_info(self,releaseContainer):
        components = []
        if releaseContainer.has_key('releaseDate'):
            components.append(releaseContainer['releaseDate'].split('T')[0])
        for key in ['country', 'primaryGenreName']:
            if releaseContainer.has_key(key):
                components.append(releaseContainer[key])
        info = u' | '.join(components)
        return info

    def get_release_instance(self,releaseContainer):
        if releaseContainer.has_key('collectionViewUrl'):
            return Release.release_from_url(releaseContainer['collectionViewUrl'])
        return None