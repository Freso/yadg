# coding=utf-8
import lxml.html
import lxml.etree
import re
from .base import Scraper, ExceptionMixin, RequestMixin, UtilityMixin, StatusCodeError, StandardFactory
from .base import SearchScraper as SearchScraperBase
from ..result import ReleaseResult, ListResult, NotFoundResult


READABLE_NAME = 'Discogs'
SCRAPER_URL = 'http://www.discogs.com/'


class ReleaseScraper(Scraper, RequestMixin, ExceptionMixin, UtilityMixin):

    _base_url = 'http://www.discogs.com/'
    string_regex = '^http://(?:www\.)?discogs\.com/(?:.+?/)?release/(\d+)$'

    ARTIST_NAME_VARIOUS = "Various"

    def __init__(self, id):
        super(ReleaseScraper, self).__init__()
        self.id = id

    def get_instance_info(self):
        return u'id="%s"' % self.id

    def get_url(self):
        return self._base_url + 'release/%s' % self.id

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
        return artist_name

    def prepare_response_content(self, content):
        #get the raw response content and parse it
        doc = lxml.html.document_fromstring(content)

        #get the div that contains all the information we want
        container = doc.cssselect('div#page_content')
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
            # handle formats with line breaks in them by replacing the linebreak with a comma
            if label == 'format':
                # ugly hack: convert the element to a string, replace all '<br>'s and parse the resulting string as HTML again
                additional_info = lxml.html.fragment_fromstring(re.sub('(?m)\s*<br(\s*/)?>(\s*<br(\s*/)?>)*', u', ', lxml.etree.tostring(additional_info)))
            #get content and remove whitespace
            content = additional_info.text_content()
            content = self.remove_whitespace(content)
            if content and (content != 'none'):
                # we might have left a lone comma at the end if we replaced some linebreaks
                if content.endswith(','):
                    content = content[:-1]
                self.additional_infos[label] = content

    def add_release_event(self):
        release_event = self.result.create_release_event()
        found = False
        if self.additional_infos.has_key('released'):
            release_event.set_date(self.additional_infos['released'])
            found = True
        if self.additional_infos.has_key('country'):
            release_event.set_country(self.additional_infos['country'])
            found = True
        if found:
            self.result.append_release_event(release_event)

    def add_release_format(self):
        if self.additional_infos.has_key('format'):
            self.result.set_format(self.additional_infos['format'])

    def add_label_ids(self):
        if self.additional_infos.has_key('label'):
            label_string = self.additional_infos['label']
            label_components = self._split_infos(label_string)

            #sometimes we have the format "label - catalog#" for a label
            for label_component in label_components:
                label_id = self.result.create_label_id()
                split = label_component.split(u' \u200e\u2013 ')
                if len(split) == 2: #we have exactely label and catalog#
                    label = self._remove_enum_suffix(split[0])
                    if split[1] != 'none':
                        catalog_nr = split[1]
                        label_id.append_catalogue_nr(catalog_nr)
                else:
                    #we just have a label or to many components, so don't change anything
                    label = self._remove_enum_suffix(label_component)
                label_id.set_label(label)
                self.result.append_label_id(label_id)

    def add_release_title(self):
        title_spans = self.container.cssselect('div.profile h1 span')
        if len(title_spans) == 0:
            self.raise_exception(u'could not find title element')
        title_span = None
        for span in title_spans:
            if u'–' in span.tail:
                title_span = span.xpath('following-sibling::span')
        if title_span is not None and len(title_span) == 1:
            title = self.remove_whitespace(title_span[0].text_content())
            if title:
                self.result.set_title(title)

    def add_release_artists(self):
        #get artist and title
        title_element = self.container.cssselect('div.profile h1')
        if len(title_element) != 1:
            self.raise_exception(u'could not find title element')
        artist_elements = title_element[0].cssselect('a')
        if len(artist_elements) == 0:
            self.raise_exception(u'could not find artist elements')
        is_feature = False
        for artist_element in artist_elements:
            artist = self.result.create_artist()
            artist_name = artist_element.text_content()
            artist_name = self.remove_whitespace(artist_name)
            artist_name = self._prepare_artist_name(artist_name)
            is_various = artist_name == self.ARTIST_NAME_VARIOUS
            if not is_various:
                artist.set_name(artist_name)
            artist.set_various(is_various)
            if is_feature:
                # we assume every artist after "feat." is a feature
                artist.append_type(self.result.ArtistTypes.FEATURING)
            else:
                artist.append_type(self.result.ArtistTypes.MAIN)
                if 'feat.' in artist_element.tail:
                    # all artists after this one are features
                    is_feature = True
            self.result.append_release_artist(artist)

    def add_genres(self):
        if self.additional_infos.has_key('genre'):
            genre_string = self.additional_infos['genre']
            for genre in map(lambda x: x.strip(' &'), self._split_infos(genre_string)):
                self.result.append_genre(genre)

    def add_styles(self):
        if self.additional_infos.has_key('style'):
            style_string = self.additional_infos['style']
            for style in map(lambda x: x.strip(' &'), self._split_infos(style_string)):
                self.result.append_style(style)

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
                if len(row.getchildren()) != 4:
                    continue
                children = row.getchildren()
                #determine cd and track number
                m = re.search('(?i)^(?:(?:(?:cd)?(\d{1,2})(?:-|\.|:))|(?:cd(?:\s+|\.|-)))?(\d+|(\w{1,2}\s?\d*)|face [ivxc]+)(?:\.)?$',children[0].text_content())
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
                disc_containers[cd_number].append({'children': children, 'track_number_string': m.group(2)})
        return disc_containers

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
            track_artist = self.result.create_artist()
            track_artist_name = track_artist_element.text_content()
            track_artist_name = self.remove_whitespace(track_artist_name)
            track_artist_name = self._prepare_artist_name(track_artist_name)
            track_artist.set_name(track_artist_name)
            track_artist.append_type(self.result.ArtistTypes.MAIN)
            track_artists.append(track_artist)
        #there might be featuring artists in the track column
        blockquote = track.cssselect('blockquote')
        if len(blockquote) == 1:
            blockquote = blockquote[0]
            extra_artist_spans = blockquote.cssselect('span.tracklist_extra_artist_span')
            for extra_artist_span in extra_artist_spans:
                span_text = extra_artist_span.text_content()
                if re.match(u'(?s).*(Featuring|Remix).*\u2013.*', span_text):
                    if u'Featuring' in span_text:
                        track_artist_type = self.result.ArtistTypes.FEATURING
                    elif u'Remix' in span_text:
                        track_artist_type = self.result.ArtistTypes.REMIXER
                    track_featuring_elements = extra_artist_span.cssselect('a')
                    for track_featuring_element in track_featuring_elements:
                        track_artist = self.result.create_artist()
                        track_feature = track_featuring_element.text_content()
                        track_feature = self.remove_whitespace(track_feature)
                        track_feature = self._prepare_artist_name(track_feature)
                        track_artist.set_name(track_feature)
                        track_artist.append_type(track_artist_type)
                        track_artists.append(track_artist)
        return track_artists

    def get_track_title(self, trackContainer):
        children = trackContainer['children']
        track = children[2]
        track_title = track.cssselect('span.tracklist_track_title')
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
            return self.seconds_from_string(track_duration)
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
            response = self.request_get(self.get_url())
        except StatusCodeError as e:
            if str(e) == "404":
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

        self.add_genres()

        self.add_styles()

        self.add_discs()

        release_url = self.get_original_string()
        if not release_url:
            release_url = self.get_url()
        if release_url:
            self.result.set_url(release_url)

        return self.result


class MasterScraper(Scraper, RequestMixin, ExceptionMixin, UtilityMixin):

    _base_url = 'http://www.discogs.com/'
    string_regex = '^http://(?:www\.)?discogs\.com/(?:.+?/)?master/(\d+)$'

    def __init__(self, id):
        super(MasterScraper, self).__init__()
        self.id = id

    def get_instance_info(self):
        return u'id="%s"' % self.id

    def get_url(self):
        return self._base_url + 'master/%s' % self.id

    def prepare_response_content(self, content):
        #get the raw response content and parse it
        self.parsed_response = lxml.html.document_fromstring(content)

    def get_artist_string(self):
        #get artist and title
        title_element = self.parsed_response.cssselect('div.profile h1')
        if len(title_element) != 1:
            self.raise_exception(u'could not find title element')
        artist_span = title_element[0].cssselect('span[itemprop="byArtist"]')
        if len(artist_span) != 1:
            self.raise_exception(u'could not find correct artist span')
        return self.remove_whitespace(artist_span[0].text_content())

    def get_release_containers(self):
        return self.parsed_response.cssselect('table.cw_releases tr.release')

    def get_release_name_and_url(self, release_container):
        release_link = release_container.cssselect('td.hl a')
        if len(release_link) == 0:
            self.raise_exception(u'could not extract release link from:' + release_container.text_content())
        release_link = release_link[0]
        release_name = release_link.text_content()
        release_name = self.remove_whitespace(release_name)
        if not release_name:
            release_name = None
        release_url = release_link.attrib['href']
        # make the release URL a fully qualified one
        if release_url.startswith('/'):
            release_url = 'http://www.discogs.com' + release_url
        m = re.match(ReleaseScraper.string_regex, release_url)
        if not m:
            release_url = None
        return release_name, release_url

    def get_release_info(self, release_container):
        #get additional info
        children = release_container.getchildren()[1:]
        components = []
        a = children[0].cssselect('a')
        if a:
            br = a[0].getnext()
            if br is not None:
                components.append(br.tail)
        children = children[1:]
        for child in children:
            components.append(child.text_content())
        components = map(self.remove_whitespace, components)
        if components:
            return u' | '.join(components)
        return None

    def get_result(self):
        response = self.request_get(url=self.get_url())
        self.prepare_response_content(self.get_response_content(response))

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

    url = 'http://www.discogs.com/search'

    def get_params(self):
        return {'type': 'release', 'q': self.search_term}

    def prepare_response_content(self, content):
        #get the raw response content and parse it
        self.parsed_response = lxml.html.document_fromstring(content)

    def get_release_containers(self):
        return self.parsed_response.cssselect('div#search_results div[data-object-type="release"] div.card_body')

    def get_release_name_and_url(self, release_container):
        title_h4 = release_container.cssselect('h4')
        if len(title_h4) != 1:
            self.raise_exception(u'could not extract title h4 from:' + release_container.text_content())
        title_h4 = title_h4[0]
        name_span = release_container.cssselect('span[itemprop="name"]')
        if len(name_span) == 0:
            self.raise_exception(u'could not find name span in:' + release_container.text_content())
        release_link = name_span[-1].getnext()
        if release_link is None:
            self.raise_exception(u'could not extract release link from:' + release_container.text_content())
        release_name = title_h4.text_content()
        release_name = self.remove_whitespace(release_name)
        if not release_name:
            release_name = None
        release_url = release_link.attrib['href']
        # make the release URL a fully qualified one
        if release_url.startswith('/'):
            release_url = 'http://www.discogs.com' + release_url
        m = re.match(ReleaseScraper.string_regex, release_url)
        if not m:
            release_url = None
        return release_name, release_url

    def get_release_info(self, release_container):
        #get additional info
        release_info = release_container.cssselect('p.card_info')
        if len(release_info) != 1:
            self.raise_exception(u'could not extract additional info from: ' + release_container.text_content())
        release_info_children = release_info[0].getchildren()
        release_info = u' | '.join(filter(lambda x: x, map(lambda x: self.remove_whitespace(x.text_content()), release_info_children)))
        if release_info:
            return release_info
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

    scraper_classes = (MasterScraper, ReleaseScraper)
    search_scraper = SearchScraper