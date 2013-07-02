# coding=utf-8
import lxml.html
import re
from .base import Scraper, ExceptionMixin, RequestMixin, UtilityMixin, StatusCodeError, StandardFactory
from .base import SearchScraper as SearchScraperBase
from ..result import ReleaseResult, ListResult, NotFoundResult


READABLE_NAME = 'Junodownload'
SCRAPER_URL = 'http://www.junodownload.com/'
NOTES = 'Track artists on VA releases are not supported.'


class ReleaseScraper(Scraper, RequestMixin, ExceptionMixin, UtilityMixin):

    _base_url = 'http://www.junodownload.com/'
    string_regex = '^http://(?:www\.)?junodownload\.com/products/([^/]*)/([^/]*)/?$'
    request_kwargs = {'allow_redirects': False}

    _various_artists_aliases = ['various']

    def __init__(self, release_name, id):
        super(ReleaseScraper, self).__init__()
        self.id = id

        self._release_name = release_name

    def get_instance_info(self):
        return u'id=%s' % self.id

    def get_url(self):
        return self._base_url + 'products/%s/%s/' % (self._release_name, self.id)

    def prepare_response_content(self, content):
        #get the raw response content and parse it
        self.parsed_response = lxml.html.document_fromstring(content)

    def add_release_event(self):
        release_date_div = self.parsed_response.cssselect('div#product_info_released_on')
        if len(release_date_div) == 1:
            release_date = release_date_div[0].text_content()
            release_date = self.remove_whitespace(release_date)
            if release_date:
                release_event = self.result.create_release_event()
                release_event.set_date(release_date)
                self.result.append_release_event(release_event)

    def add_label_ids(self):
        cat_nr_div = self.parsed_response.cssselect('div#product_info_cat_no')
        cat_nr = None
        if len(cat_nr_div) == 1:
            cat_nr = cat_nr_div[0].text_content()
            cat_nr = self.remove_whitespace(cat_nr)
        label_anchors = self.parsed_response.cssselect('div#product_heading_label a[itemprop="author"]')
        for label_anchor in label_anchors:
            label_name = label_anchor.text_content()
            label_name = self.remove_whitespace(label_name)
            if label_name:
                label_id = self.result.create_label_id()
                label_id.set_label(label_name)
                if cat_nr:
                    label_id.append_catalogue_nr(cat_nr)
                self.result.append_label_id(label_id)

    def add_release_title(self):
        title_anchor = self.parsed_response.cssselect('div#product_heading_title a[itemprop="name"]')
        if len(title_anchor) != 1:
            self.raise_exception(u'could not get release title anchor')
        title = title_anchor[0].text_content()
        title = self.remove_whitespace(title)
        if title:
            self.result.set_title(title)

    def add_release_artists(self):
        in_breadcrumbs = True
        artist_anchors = self.parsed_response.cssselect('div#topbar_bread div.breadcrumb_text h1 a')
        artist_anchors = filter(lambda x: x.attrib['href'].startswith('/artists/'), artist_anchors)
        if not artist_anchors:
            #apparently the artist is not always part of the breadcrumbs
            artist_anchors = self.parsed_response.cssselect('div#product_heading_artist a')
            artist_anchors = filter(lambda x: x.attrib['href'].startswith('/artists/'), artist_anchors)
            in_breadcrumbs = False
        is_feature = False
        has_various = False
        for artist_anchor in artist_anchors:
            artist_name = artist_anchor.text_content()
            artist_name = self.remove_whitespace(artist_name)
            if not in_breadcrumbs:
                #do some rudimentary capitalizing if we did not get the artists from the breadcrumbs
                artist_name = u' '.join(map(lambda x: x.capitalize(), artist_name.split()))
            if artist_name.lower() in self._various_artists_aliases:
                has_various = True
            elif artist_name:
                artist = self.result.create_artist()
                artist.set_name(artist_name)
                if is_feature:
                    artist.append_type(self.result.ArtistTypes.FEATURING)
                else:
                    artist.append_type(self.result.ArtistTypes.MAIN)
                self.result.append_release_artist(artist)
            if not is_feature and artist_anchor.tail and 'feat' in artist_anchor.tail:
                # all artists after this one are features
                is_feature = True
        if not self.result.get_release_artists() and has_various:
            # only add the 'Various' to artists if it is the only one
            artist = self.result.create_artist()
            artist.set_various(True)
            artist.append_type(self.result.ArtistTypes.MAIN)
            self.result.append_release_artist(artist)

    def add_genres(self):
        genre_anchors = self.parsed_response.cssselect('div#product_info_genre a')
        for genre_anchor in genre_anchors:
            genre_string = genre_anchor.text_content()
            genre_strings = genre_string.split('/')
            genre_strings = filter(lambda x: x, map(self.remove_whitespace, genre_strings))
            for genre in genre_strings:
                self.result.append_genre(genre)

    def get_disc_containers(self):
        tracklist_div = self.parsed_response.cssselect('div#product_tracklist')
        if len(tracklist_div) != 1:
            self.raise_exception(u'could not find tracklist div')
        return {1: tracklist_div[0]}

    def get_track_containers(self, disc_container):
        return disc_container.cssselect('div.product_tracklist_records[itemprop="tracks"]')

    def get_track_number(self, track_container):
        track_nr_div = track_container.cssselect('div.product_tracklist_heading_records_sn')
        if len(track_nr_div) != 1:
            self.raise_exception(u'could not find track number div')
        track_nr = track_nr_div[0].text_content()
        track_nr = self.remove_whitespace(track_nr)
        if track_nr:
            return track_nr
        return None

    def get_track_title(self, track_container):
        title_div = track_container.cssselect('div.product_tracklist_heading_records_title[itemprop="name"]')
        if len(title_div) != 1:
            self.raise_exception(u'could not find title div')
        title = title_div[0].text_content()
        title = self.remove_whitespace(title)
        if title:
            return title
        return None

    def get_track_length(self, trackContainer):
        length_div = trackContainer.cssselect('div.product_tracklist_heading_records_length')
        if len(length_div) == 1:
            length = length_div[0].text_content()
            length = self.remove_whitespace(length)
            if length:
                i = 0
                length_s = 0
                for component in reversed(length.split(':')):
                    length_s += int(component) * 60**i
                    i += 1
                return length_s
        return None

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

                disc.append_track(track)
            self.result.append_disc(disc)

    def get_result(self):
        try:
            response = self.request_get(self.get_url())
        except StatusCodeError as e:
            # non existent release pages are automatically forwarded to a search
            # make sure we return a NotFoundResult in that case
            if str(e) == "404" or str(e) == "302":
                self.result = NotFoundResult()
                self.result.set_scraper_name(self.get_name())
                return self.result
            else:
                self.raise_exception("request to server unsuccessful, status code: %s" % str(e))

        self.result = ReleaseResult()
        self.result.set_scraper_name(self.get_name())

        self.prepare_response_content(self.get_response_content(response))

        self.add_release_event()

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

    _base_url = 'http://www.junodownload.com'
    url = 'http://www.junodownload.com/betasearch/'

    def get_params(self):
        return {'solrorder': 'relevancy', 'submit-search': 'SEARCH', 'q[all][]': self.search_term}

    def prepare_response_content(self, content):
        #get the raw response content and parse it
        self.parsed_response = lxml.html.document_fromstring(content)

    def get_release_containers(self):
        return self.parsed_response.cssselect('div.productlist_widget_product_detail')[:25]

    def get_release_name(self, releaseContainer):
        components = []
        release_artist_div = releaseContainer.cssselect('div.productlist_widget_product_artists')
        if len(release_artist_div) == 1:
            release_artists = release_artist_div[0].text_content()
            release_artists = self.remove_whitespace(release_artists)
            if release_artists:
                release_artists = u', '.join(release_artists.split('/'))
                components.append(release_artists)
        release_title_div = releaseContainer.cssselect('div.productlist_widget_product_title')
        if len(release_title_div) == 1:
            release_title = release_title_div[0].text_content()
            release_title = self.remove_whitespace(release_title)
            if release_title:
                components.append(release_title)
        if components:
            return u' \u2013 '.join(components)
        self.raise_exception(u'could not determine release name')

    def get_release_info(self, releaseContainer):
        components = []
        label_div = releaseContainer.cssselect('div.productlist_widget_product_label')
        if len(label_div) == 1:
            label = label_div[0].text_content()
            label = self.remove_whitespace(label)
            if label:
                components.append(label)
        additional_info_div = releaseContainer.cssselect('div.productlist_widget_product_preview_buy')
        if len(additional_info_div) == 1:
            additional_info = additional_info_div[0].text_content()
            additional_infos = additional_info.split('\n')
            additional_infos = filter(lambda x: x, map(self.remove_whitespace, additional_infos))
            if additional_infos:
                components.extend(additional_infos)
        if components:
            return u' | '.join(components)
        return None

    def get_release_url(self, releaseContainer):
        release_anchor = releaseContainer.cssselect('div.productlist_widget_product_title span a')
        if len(release_anchor) != 1:
            self.raise_exception(u'could not find release link anchor')
        release_link = self._base_url + release_anchor[0].attrib['href']
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