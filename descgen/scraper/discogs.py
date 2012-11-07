# coding=utf-8
import lxml.html,re,lxml.etree
from base import BaseSearch, BaseRelease, BaseAPIError

READABLE_NAME = 'Discogs'


class DiscogsAPIError(BaseAPIError):
    pass


class Release(BaseRelease):

    _base_url = 'http://www.discogs.com/'
    url_regex = '^http://(?:www\.)?discogs\.com/(?:.+?/)?release/(\d+)$'
    exception = DiscogsAPIError

    def __init__(self, id):
        self.id = id

    def __unicode__(self):
        return u'<DiscogsRelease: id="' + str(self.id) + u'">'

    @staticmethod
    def _get_args_from_match(match):
        return (int(match.group(1)), )

    def get_url(self):
        return self._base_url + 'release/%d' % self.id

    def get_release_url(self):
        return self.get_url()

    def _split_infos(self, info_string):
        components = info_string.split(',')
        #remove leading and trailing whitespace
        components = map(lambda x: x.strip(), components)
        #remove empty elements
        components = filter(lambda x: x, components)
        return components

    def _remove_enum_suffix(self, string):
        return re.sub(u'(.*) \(\d+\)$', r'\1', string)

    def _prepare_artist_name(self, artist_name):
        artist_name = self._remove_enum_suffix(artist_name)
        artist_name = self.swap_suffix(artist_name)
        if artist_name == 'Various':
            artist_name = self.ARTIST_NAME_VARIOUS
        return artist_name

    def prepare_response_content(self, content):
        #get the raw response content and parse it
        doc = lxml.html.document_fromstring(content)

        #get the div that contains all the information we want
        container = doc.cssselect('div#page > div.lr > div.left')
        if len(container) != 1:
            self.raise_exception(u'could not find anchor point')
        self.container = container[0]

        #get additional infos
        self.additional_infos = {}
        additional_infos = self.container.cssselect('div.head + div.content')
        for additional_info in additional_infos:
            label_element = additional_info.getprevious()
            #get label and remove whitespace and ':'
            label = label_element.text_content()
            label = self.remove_whitespace(label)
            #make sure only valid keys are present
            label = re.sub('\W','',label)
            label = label.lower()
            #get content and remove whitespace
            content = additional_info.text_content()
            content = self.remove_whitespace(content)
            if content and (content != 'none'):
                self.additional_infos[label] = content

    def get_release_date(self):
        if self.additional_infos.has_key('released'):
            return self.additional_infos['released']
        return None

    def get_release_format(self):
        if self.additional_infos.has_key('format'):
            return self.additional_infos['format']
        return None

    def get_labels(self):
        if self.additional_infos.has_key('label'):
            label_string = self.additional_infos['label']
            label_components = self._split_infos(label_string)

            labels = []
            #sometimes we have the format "label - catalog#" for a label
            for label_component in label_components:
                split = label_component.split(u' \u2013 ')
                if len(split) == 2: #we have exactely label and catalog#
                    label = self._remove_enum_suffix(split[0])
                else:
                    #we just have a label or to many components, so don't change anything
                    label = self._remove_enum_suffix(label_component)
                labels.append(label)
            return labels
        return []

    def get_catalog_numbers(self):
        if self.additional_infos.has_key('label'):
            label_string = self.additional_infos['label']
            label_components = self._split_infos(label_string)

            catalog_nr = []
            #sometimes we have the format "label - catalog#" for a label
            for label_component in label_components:
                split = label_component.split(u' \u2013 ')
                if len(split) == 2 and split[1] != 'none': #we have exactely label and catalog#
                    catalog_nr.append(split[1])
            return catalog_nr
        return []

    def get_release_title(self):
        title_element = self.container.cssselect('div.profile h1')
        if len(title_element) != 1:
            self.raise_exception(u'could not find title element')
        title_element = title_element[0]
        title = title_element.text_content()
        #right now this contains 'artist - title', so remove 'artist'
        title = title.split(u'–')
        if len(title) != 2:
            self.raise_exception('could not split release title')
        title = self.remove_whitespace(title[1])
        if title:
            return title
        return None

    def get_release_country(self):
        if self.additional_infos.has_key('country'):
            return self.additional_infos['country']
        return None

    def get_release_artists(self):
        #get artist and title
        title_element = self.container.cssselect('div.profile h1')
        if len(title_element) != 1:
            self.raise_exception(u'could not find title element')
        artist_elements = title_element[0].cssselect('a')
        if len(artist_elements) == 0:
            self.raise_exception(u'could not find artist elements')
        artists = []
        is_feature = False
        for artist_element in artist_elements:
            artist = artist_element.text_content()
            artist = self.remove_whitespace(artist)
            artist = self._prepare_artist_name(artist)
            if is_feature:
                # we assume every artist after "feat." is a feature
                artist_type = self.ARTIST_TYPE_FEATURE
            else:
                artist_type = self.ARTIST_TYPE_MAIN
                if 'feat.' in artist_element.tail:
                    # all artists after this one are features
                    is_feature = True
            artists.append(self.format_artist(artist, artist_type))
        return artists

    def get_genres(self):
        if self.additional_infos.has_key('genre'):
            genre_string = self.additional_infos['genre']
            return map(lambda x: x.strip(' &'),self._split_infos(genre_string))
        return []

    def get_styles(self):
        if self.additional_infos.has_key('style'):
            style_string = self.additional_infos['style']
            return map(lambda x: x.strip(' &'),self._split_infos(style_string))
        return []

    def get_disc_containers(self):
        disc_containers = {}
        tracklist_tables = self.container.cssselect('div#tracklist table')
        if not tracklist_tables:
            self.raise_exception(u'could not find tracklisting')
        for table in tracklist_tables:
            rows = table.cssselect('tr')
            if not rows:
                self.raise_exception(u'could not find track information')
            for row in rows:
                #ignore rows that don't have the right amount of columns
                if len(row.getchildren()) != 5:
                    continue
                children = row.getchildren()
                #determine cd and track number
                m = re.search('(?i)^(?:(?:(?:cd)?(\d{1,2})(?:-|\.|:))|(?:cd(?:\s+|\.|-)))?(\d+|(\w{1,2}\s?\d*))(?:\.)?$',children[0].text_content())
                if not m:
                    #ignore tracks with strange track number
                    continue
                cd_number = m.group(1)
                #if there is no cd number we default to 1
                if not cd_number:
                    cd_number = 1
                else:
                    cd_number = int(cd_number)
                if not disc_containers.has_key(cd_number):
                    disc_containers[cd_number] = []
                disc_containers[cd_number].append({'children':children, 'track_number_string':m.group(2)})
        return disc_containers

    def get_track_containers(self, discContainer):
        return discContainer

    def get_track_number(self, trackContainer):
        number = trackContainer['track_number_string']
        if not re.search('\D',number):
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
        children = trackContainer['children']
        track_artists_column = children[1]
        track = children[2]
        #get track artist
        track_artists_elements = track_artists_column.cssselect('a')
        track_artists = []
        for track_artist_element in track_artists_elements:
            track_artist = track_artist_element.text_content()
            track_artist = self.remove_whitespace(track_artist)
            track_artist = self._prepare_artist_name(track_artist)
            track_artists.append(self.format_artist(track_artist, self.ARTIST_TYPE_MAIN))
        #there might be featuring artists in the track column
        blockquote = track.cssselect('blockquote')
        if len(blockquote) == 1:
            blockquote = blockquote[0]
            extra_artist_spans = blockquote.cssselect('span.tracklist_extra_artist_span')
            for extra_artist_span in extra_artist_spans:
                span_text = extra_artist_span.text_content()
                if re.match(u'(?s).*(Featuring|Remix).*\u2013.*', span_text):
                    if u'Featuring' in span_text:
                        track_artist_type = self.ARTIST_TYPE_FEATURE
                    elif u'Remix' in span_text:
                        track_artist_type = self.ARTIST_TYPE_REMIXER
                    track_featuring_elements = extra_artist_span.cssselect('a')
                    for track_featuring_element in track_featuring_elements:
                        track_feature = track_featuring_element.text_content()
                        track_feature = self.remove_whitespace(track_feature)
                        track_feature = self._prepare_artist_name(track_feature)
                        track_artists.append(self.format_artist(track_feature, track_artist_type))
        return track_artists

    def get_track_title(self, trackContainer):
        children = trackContainer['children']
        track = children[2]
        track_title = track.cssselect('span.track_title')
        if len(track_title) != 1:
            self.raise_exception(u'could not determine track title')
        track_title = track_title[0].text_content()
        track_title = self.remove_whitespace(track_title)
        if track_title:
            return track_title
        return None

    def get_track_length(self, trackContainer):
        children = trackContainer['children']
        track_duration = children[3]
        track_duration = track_duration.text_content()
        track_duration = self.remove_whitespace(track_duration)
        if track_duration:
            return track_duration
        return None


class Search(BaseSearch):

    url = 'http://www.discogs.com/search'
    exception = DiscogsAPIError

    def __unicode__(self):
        return u'<DiscogsSearch: term="' + self.search_term + u'">'

    def get_params(self):
        return {'type':'release', 'q':self.search_term}

    def prepare_response_content(self, content):
        #get the raw response content and parse it
        self.parsed_response = lxml.html.document_fromstring(content)

    def get_release_containers(self):
        return self.parsed_response.cssselect('ol.search_results li.body_row div.result_container')

    def get_release_name(self,releaseContainer):
        release_link = releaseContainer.cssselect('a.search_result_title')
        if len(release_link) != 1:
            self.raise_exception(u'could not extract release link from:' + releaseContainer.text_content())
        release_link = release_link[0]
        release_name = release_link.text_content()
        release_name = self.remove_whitespace(release_name)
        if release_name:
            return release_name
        return None

    def get_release_info(self,releaseContainer):
        #get additional info
        release_info = releaseContainer.cssselect('span.push_right_mini')
        release_info = filter(lambda x: not x.text_content() in ("Release", "Master Release"), release_info)
        if len(release_info) != 1:
            self.raise_exception(u'could not extract additional info from: ' + releaseContainer.text_content())
        release_info = release_info[0].text_content()
        release_info = u' | '.join(map(lambda x: self.remove_whitespace(x), release_info.split(u'·')))
        if release_info:
            return release_info
        return None

    def get_release_instance(self,releaseContainer):
        release_link = releaseContainer.cssselect('a.search_result_title')
        if len(release_link) != 1:
            self.raise_exception(u'could not extract release link from:' + releaseContainer.text_content())
        release_link = release_link[0]
        href = release_link.attrib['href']
        # make the release URL a fully qualified one
        if href.startswith('/'):
            href = 'http://www.discogs.com' + href
        return Release.release_from_url(href)