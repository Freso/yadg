# coding=utf-8
import lxml.html,re,json
from base import BaseRelease, BaseSearch, BaseAPIError


READABLE_NAME = 'Metal-Archives'


class MetalarchivesAPIError(BaseAPIError):
    pass


class Release(BaseRelease):

    _base_url = 'http://www.metal-archives.com/'
    url_regex = '^http://(?:www\.)?metal-archives\.com/albums/(.*?)/(.*?)/(\d+)$'
    exception = MetalarchivesAPIError

    def __init__(self, id, release_artist = '', release_name = ''):
        self.id = id

        self._release_artist = release_artist
        self._release_name = release_name

        self._info_dict = None

    def __unicode__(self):
        return u'<MetalarchivesRelease: id=%d>' % self.id

    @staticmethod
    def _get_args_from_match(match):
        return (int(match.group(3)), match.group(1), match.group(2))

    def get_url(self):
        return self._base_url + 'albums///%d' % self.id

    def get_release_url(self):
        return self._base_url + 'albums/%s/%s/%d' %(self._release_artist,self._release_name,self.id)

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
                    if dt =='Type:':
                        self._info_dict['format'] = dd
                    elif dt == 'Release date:':
                        self._info_dict['released'] = dd
                    elif dt =='Label:':
                        self._info_dict['label'] = [dd,]
        return self._info_dict

    def prepare_response_content(self, content):
        #get the raw response content and parse it
        #we explicitely decode the response content to unicode
        self.parsed_response = lxml.html.document_fromstring(content.decode('utf-8'))

        #stupid website doesn't send correct http status code
        h3_404 = self.parsed_response.cssselect('h3')
        for candidate in h3_404:
            if candidate.text_content() == 'Error 404':
                self.raise_exception(u'404')

    def get_release_date(self):
        info_dict = self._get_info_dict()
        if info_dict.has_key('released'):
            return info_dict['released']
        return None

    def get_release_format(self):
        info_dict = self._get_info_dict()
        if info_dict.has_key('format'):
            return info_dict['format']
        return None

    def get_labels(self):
        info_dict = self._get_info_dict()
        if info_dict.has_key('label'):
            return info_dict['label']
        return []

    def get_release_title(self):
        title_h1 = self.parsed_response.cssselect('div#album_info h1.album_name')
        if len(title_h1) != 1:
            self.raise_exception(u'could not find album title h1')
        title_h1 = title_h1[0]
        return self.remove_whitespace(title_h1.text_content())

    def get_release_artists(self):
        artists_h2 = self.parsed_response.cssselect('div#album_info h2.band_name')
        if len(artists_h2) == 0:
            self.raise_exception(u'could not find artist h2')
        artists = []
        for artist_h2 in artists_h2:
            artist_name = self.remove_whitespace(artist_h2.text_content())
            artists.append(self.format_artist(artist_name, self.ARTIST_TYPE_MAIN))
        return artists

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
                m = re.match('(?:Disc|CD) (\d+)',header)
                if m:
                    disc_number = int(m.group(1))
            elif len(columns) == 4:
                if not disc_containers.has_key(disc_number):
                    disc_containers[disc_number] = []

                disc_containers[disc_number].append(columns)
            else:
                continue
        return disc_containers

    def get_track_containers(self, discContainer):
        return discContainer

    def get_track_number(self, trackContainer):
        (track_number_td,track_title_td,track_length_td,lyrics_td) = trackContainer
        m = re.search('(\d+)(?:\.)?',track_number_td.text_content())
        if m:
            track_number_without_zeros = m.group(1).lstrip('0')
            if track_number_without_zeros:
                track_number = track_number_without_zeros
            else:
                track_number = '0'
        else:
            self.raise_exception(u'could not extract track number')
        return track_number

    def get_track_title(self, trackContainer):
        (track_number_td,track_title_td,track_length_td,lyrics_td) = trackContainer
        track_title = self.remove_whitespace(track_title_td.text_content())
        return track_title

    def get_track_length(self, trackContainer):
        (track_number_td,track_title_td,track_length_td,lyrics_td) = trackContainer
        track_length = self.remove_whitespace(track_length_td.text_content())
        return track_length


class Search(BaseSearch):

    url = 'http://www.metal-archives.com/search/ajax-album-search/'
    exception = MetalarchivesAPIError

    def __unicode__(self):
        return u'<MetalarchivesSearch: term="' + self.search_term + u'">'

    def get_params(self):
        return {'field':'title', 'query':self.search_term}

    def prepare_response_content(self, content):
        try:
            self.parsed_response = json.loads(content)
        except:
            self.raise_exception(u'invalid server response')

    def get_release_containers(self):
        if self.parsed_response.has_key('aaData'):
            return self.parsed_response['aaData'][:25]
        return []

    def get_release_name(self,releaseContainer):
        (artists_html,title_html,type,date_html) = releaseContainer
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

        return u', '.join(artists) + u' \u2013 ' + title

    def get_release_info(self,releaseContainer):
        (artists_html,title_html,type,date_html) = releaseContainer
        date_div = lxml.html.fragment_fromstring(date_html, create_parent="div")

        date = date_div.text_content()
        date = self.remove_whitespace(date)

        info_components = filter(lambda x: x, [date,type])

        return u' | '.join(info_components)

    def get_release_instance(self,releaseContainer):
        (artists_html,title_html,type,date_html) = releaseContainer
        title_div = lxml.html.fragment_fromstring(title_html, create_parent="div")
        title_a = title_div.cssselect('a')
        if len(title_a) != 1:
            self.raise_exception(u'could not extract release title')
        title_a = title_a[0]
        return Release.release_from_url(title_a.attrib['href'])