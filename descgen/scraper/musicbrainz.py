# coding=utf-8
import lxml.html,re
from base import BaseAPIError, BaseRelease, BaseSearch


READABLE_NAME = 'Musicbrainz'


class MusicBrainzAPIError(BaseAPIError):
    pass


class Release(BaseRelease):

    _base_url = 'http://musicbrainz.org/'
    url_regex = '^http://(?:www\.)?musicbrainz.org/release/([A-Za-z0-9\-]+)$'
    exception = MusicBrainzAPIError

    def __init__(self, id):
        self.id = id

        self._labels = None
        self._catalogs = None

    def __unicode__(self):
        return u'<MusicBrainzRelease: id="' + self.id + u'">'

    def get_url(self):
        return self._base_url + 'release/%s' % self.id

    def get_release_url(self):
        return self.get_url()

    def raise_exception(self, message):
        # MusicBrainz throws a 400 BAD REQUEST if the ID is malformed
        # to make sure we catch this as a 404 error, we rewrite the message
        if message == '400':
            message = '404'
        return super(Release, self).raise_exception(message)

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

    def _get_labels_and_catalogs(self):
        if self._labels is None:
            if self._sidebar_captions.has_key('Labels'):
                caption = self._sidebar_captions['Labels']

                label_ul = caption.getnext()
                label_li = label_ul.cssselect('li')

                if len(label_li) != 0:
                    self._labels = []

                for li in label_li:
                    label_a = li.cssselect('a[rel="mo:label"]')
                    if len(label_a) == 1:
                        label_a = label_a[0]
                    else:
                        #if we cannot find the label we assume something is wrong
                        self.raise_exception('could not find label link in label li')

                    catalog_span = li.cssselect('span[property="mo:catalogue_number"]')
                    if len(catalog_span) == 1:
                        catalog_span = catalog_span[0]
                    else:
                        catalog_span = None

                    self._labels.append(self.remove_whitespace(label_a.text_content()))
                    if catalog_span is not None:
                        catalog_span_content = self.remove_whitespace(catalog_span.text_content())
                        if catalog_span_content:
                            if self._catalogs is None:
                                self._catalogs = []
                            self._catalogs.append(catalog_span_content)
        return (self._labels, self._catalogs)

    def prepare_response_content(self, content):
        #get the raw response content and parse it
        #we explicitely decode the response content to unicode
        self.parsed_response = lxml.html.document_fromstring(content.decode('utf-8'))

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


    def get_release_date(self):
        if self._sidebar_captions.has_key('Release information'):
            caption = self._sidebar_captions['Release information']

            dl = caption.getnext()
            dd = self._get_dd_from_dt('Date:', dl.getchildren())

            if dd is not None:
                return self.remove_whitespace(dd.text_content())
        return None

    def get_release_format(self):
        if self._sidebar_captions.has_key('Release information'):
            caption = self._sidebar_captions['Release information']

            dl = caption.getnext()
            children = dl.getchildren()
            dd_format = self._get_dd_from_dt('Format:', children)
        else:
            dd_format = None

        if self._sidebar_captions.has_key('Additional details'):
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
            return format
        return None

    def get_labels(self):
        labels, catalogs = self._get_labels_and_catalogs()
        if labels:
            return labels
        return []

    def get_catalog_numbers(self):
        labels, catalogs = self._get_labels_and_catalogs()
        if catalogs:
            return catalogs
        return []

    def get_release_title(self):
        title_a = self._release_header_div.cssselect('h1 a')
        if len(title_a) != 1:
            self.raise_exception(u'could not find release title a')
        title_a = title_a[0]

        return self.remove_whitespace(title_a.text_content())

    def get_release_country(self):
        if self._sidebar_captions.has_key('Release information'):
            caption = self._sidebar_captions['Release information']

            dl = caption.getnext()
            dd = self._get_dd_from_dt('Country:', dl.getchildren())

            if dd is not None:
                return self.remove_whitespace(dd.text_content())
        return None

    def get_release_artists(self):
        artist_links = self._release_header_div.cssselect('p.subheader > a')
        if len(artist_links) == 0:
            self.raise_exception(u'could not find artist a')

        artists = []
        for artist_a in artist_links:
            artist = self.remove_whitespace(artist_a.text_content())
            if artist == 'Various Artists':
                artist = self.ARTIST_NAME_VARIOUS
            artists.append(self.format_artist(artist, self.ARTIST_TYPE_MAIN))
        return artists

    def get_disc_containers(self):
        if self._tracklist_caption is not None:
            tracklist_table = self._tracklist_caption.getnext()
            disc_divs = tracklist_table.cssselect('tbody > div')
            if len(disc_divs) == 0:
                self.raise_exception(u'could not find any disc tracklisting')
            discs_containers = {}
            for disc_div in disc_divs:
                caption_tr = disc_div.getprevious()
                caption_a = caption_tr.cssselect('a')
                if len(caption_a) != 1:
                    self.raise_exception(u'could not determine disc header')
                caption_a = caption_a[0]
                m = re.search('\d+',caption_a.text_content())
                if not m:
                    self.raise_exception(u'could not determine disc number')
                disc_number = int(m.group(0))
                discs_containers[disc_number] = {'div':disc_div, 'caption':caption_a.text_content()}
            return discs_containers
        return {}

    def get_disc_title(self, discContainer):
        caption = discContainer['caption']
        caption = u':'.join(caption.split(u':')[1:])
        caption = self.remove_whitespace(caption)
        if caption:
            return caption
        return None

    def get_track_containers(self, discContainer):
        track_rows = discContainer['div'].cssselect('span > tr')
        return map(lambda x: x.cssselect('td'), track_rows)

    def get_track_number(self, trackContainer):
        if len(trackContainer) in (4, 5):
            track_number_td = trackContainer[0]
        else:
            self.raise_exception(u'track row has not the right amount of columns')

        track_number_span = track_number_td.cssselect('span[property="mo:track_number"]')
        if len(track_number_span) != 1:
            self.raise_exception(u'could not get tracknumber')
        track_number_span = track_number_span[0]
        track_number = self.remove_whitespace(track_number_span.text_content())

        #remove leading zeros from track number
        if track_number.lstrip('0'):
            track_number = track_number.lstrip('0')
        else:
            track_number = '0'
        return track_number

    def get_track_artists(self, trackContainer):
        if len(trackContainer) == 4:
            artist_td = None
        elif len(trackContainer) == 5:
            artist_td = trackContainer[2]
        else:
            self.raise_exception(u'track row has not the right amount of columns')
        track_artists = []
        if artist_td is not None:
            track_artist_links = artist_td.cssselect('a')
            if len(track_artist_links) == 0:
                self.raise_exception(u'could not get track artists')
            for track_artist_a in track_artist_links:
                track_artist = self.remove_whitespace(track_artist_a.text_content())
                if track_artist == 'Various Artists':
                    track_artist = self.ARTIST_NAME_VARIOUS
                if not track_artist in track_artists:
                    track_artists.append(self.format_artist(track_artist, self.ARTIST_TYPE_MAIN))
        return track_artists

    def get_track_title(self, trackContainer):
        if len(trackContainer) in (4, 5):
            title_td = trackContainer[1]
        else:
            self.raise_exception(u'track row has not the right amount of columns')
        title_a = title_td.cssselect('a[rel="mo:publication_of"]')
        if len(title_a) != 1:
            self.raise_exception(u'could not get track title')
        title_a = title_a[0]
        track_title = self.remove_whitespace(title_a.text_content())
        return track_title

    def get_track_length(self, trackContainer):
        if len(trackContainer) in (4, 5):
            length_td = trackContainer[-1]
        else:
            self.raise_exception(u'track row has not the right amount of columns')
        length_span = length_td.cssselect('span[property="mo:duration"]')
        if len(length_span) != 1:
            self.raise_exception(u'could not get track length')
        length_span = length_span[0]
        track_length = self.remove_whitespace(length_span.text_content())

        #make sure the track length is valid
        if '?' in track_length:
            track_length = None
        return track_length


class Search(BaseSearch):

    url = 'http://musicbrainz.org/search'
    exception = MusicBrainzAPIError

    def __unicode__(self):
        return u'<MusicBrainzSearch: term="' + self.search_term + u'">'

    def get_params(self):
        return {'type':'release', 'limit':'25', 'query':self.search_term}

    def prepare_response_content(self, content):
        #get the raw response content and parse it
        #we explicitely decode the response content to unicode
        content = content.decode('utf-8')
        self.parsed_response = lxml.html.document_fromstring(content)

    def get_release_containers(self):
        result_table = self.parsed_response.cssselect('div#content table.tbl')

        if len(result_table) != 1:
            #no results
            return []
        result_table = result_table[0]

        return map(lambda x: x.getchildren(), result_table.cssselect('tbody tr'))

    def get_release_name(self,releaseContainer):
        title_col = releaseContainer[1]
        artist_col = releaseContainer[2]
        title_a = title_col.cssselect('a')
        if len(title_a) != 1:
            self.raise_exception(u'could not determine release title')
        title_a = title_a[0]
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
            if artist == u'Various Artists':
                artist = Release.ARTIST_NAME_VARIOUS
            artists.append(artist)
        if len(artists) != 0 or title:
            name = u', '.join(artists)
            if name:
                name += u' \u2013 '
            name += title
            return name
        return None

    def get_release_info(self,releaseContainer):
        track_count_col = releaseContainer[3]
        country_col = releaseContainer[4]
        #get track count
        track_count = self.remove_whitespace(track_count_col.text_content())
        #get country
        country = self.remove_whitespace(country_col.text_content())
        info = u''
        if country:
            info += u'Country: ' + country
            if track_count:
                info += u' | '
        if track_count:
            info += track_count + u' Tracks'
        if info:
            return info
        return None

    def get_release_instance(self,releaseContainer):
        title_col = releaseContainer[1]
        title_a = title_col.cssselect('a')
        if len(title_a) != 1:
            self.raise_exception(u'could not determine release title')
        title_a = title_a[0]
        #get release object
        return Release.release_from_url(title_a.attrib['href'])