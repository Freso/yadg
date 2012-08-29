# coding=utf-8
import lxml.html
from base import BaseRelease, BaseSearch, BaseAPIError


READABLE_NAME = 'Junodownload'


class JunodownloadAPIError(BaseAPIError):
    pass


class Release(BaseRelease):

    _base_url = 'http://www.junodownload.com/'
    url_regex = '^http://(?:www\.)?junodownload\.com/products/([^/]*)/([^/]*)/?$'
    exception = JunodownloadAPIError
    request_kwargs = {'allow_redirects':False}

    _various_artists_aliases = ['various']

    def __init__(self, release_name, id):
        self.id = id

        self._release_name = release_name

    def __unicode__(self):
        return u'<JunodownloadRelease: id=%s>' % self.id

    def get_url(self):
        return self._base_url + 'products/%s/%s/' % (self._release_name, self.id)

    def get_release_url(self):
        return self.get_url()

    def get_response(self):
        try:
            return super(Release, self).get_response()
        except self.exception as e:
            # non existent release pages are automatically forwarded to a search
            # make sure we throw a 404 if that occurs
            if unicode(e).startswith(u"302"):
                self.raise_exception(u'404')
            else:
                raise e

    def prepare_response_content(self, content):
        #get the raw response content and parse it
        self.parsed_response = lxml.html.document_fromstring(content)

    def get_release_date(self):
        release_date_div = self.parsed_response.cssselect('div#product_info_released_on')
        if len(release_date_div) == 1:
            release_date = release_date_div[0].text_content()
            release_date = self.remove_whitespace(release_date)
            if release_date:
                return release_date
        return None

    def get_labels(self):
        label_anchors = self.parsed_response.cssselect('div#product_heading_label a[itemprop="author"]')
        labels = []
        for label_anchor in label_anchors:
            label_name = label_anchor.text_content()
            label_name = self.remove_whitespace(label_name)
            if label_name:
                labels.append(label_name)
        return labels

    def get_catalog_numbers(self):
        cat_nr_div = self.parsed_response.cssselect('div#product_info_cat_no')
        cat_nrs = []
        if len(cat_nr_div) == 1:
            cat_nr = cat_nr_div[0].text_content()
            cat_nr = self.remove_whitespace(cat_nr)
            if cat_nr:
                cat_nrs.append(cat_nr)
        return cat_nrs

    def get_release_title(self):
        title_anchor = self.parsed_response.cssselect('div#product_heading_title a[itemprop="name"]')
        if len(title_anchor) != 1:
            self.raise_exception(u'could not get release title anchor')
        title = title_anchor[0].text_content()
        title = self.remove_whitespace(title)
        if title:
            return title
        return None

    def get_release_artists(self):
        in_breadcrumbs = True
        artist_anchors = self.parsed_response.cssselect('div#topbar_bread div.breadcrumb_text h1 a')
        artist_anchors = filter(lambda x: x.attrib['href'].startswith('/artists/'), artist_anchors)
        if not artist_anchors:
            #apparently the artist is not always part of the breadcrumbs
            artist_anchors = self.parsed_response.cssselect('div#product_heading_artist a')
            artist_anchors = filter(lambda x: x.attrib['href'].startswith('/artists/'), artist_anchors)
            in_breadcrumbs = False
        artists = []
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
                if is_feature:
                    artists.append(self.format_artist(artist_name, self.ARTIST_TYPE_FEATURE))
                else:
                    artists.append(self.format_artist(artist_name, self.ARTIST_TYPE_MAIN))
            if not is_feature and artist_anchor.tail and 'feat' in artist_anchor.tail:
                # all artists after this one are features
                is_feature = True
        if not artists and has_various:
            # only add the 'Various' to artists if it is the only one
            artists.append(self.format_artist(self.ARTIST_NAME_VARIOUS, self.ARTIST_TYPE_MAIN))
        return artists

    def get_genres(self):
        genre_anchors = self.parsed_response.cssselect('div#product_info_genre a')
        genres = []
        for genre_anchor in genre_anchors:
            genre_string = genre_anchor.text_content()
            genre_strings = genre_string.split('/')
            genre_strings = filter(lambda x: x, map(self.remove_whitespace, genre_strings))
            if genre_strings:
                genres.extend(genre_strings)
        return genres

    def get_disc_containers(self):
        tracklist_div = self.parsed_response.cssselect('div#product_tracklist')
        if len(tracklist_div) != 1:
            self.raise_exception(u'could not find tracklist div')
        return {1:tracklist_div[0]}

    def get_track_containers(self, discContainer):
        return discContainer.cssselect('div.product_tracklist_records[itemprop="tracks"]')

    def get_track_number(self, trackContainer):
        track_nr_div = trackContainer.cssselect('div.product_tracklist_heading_records_sn')
        if len(track_nr_div) != 1:
            self.raise_exception(u'could not find track number div')
        track_nr = track_nr_div[0].text_content()
        track_nr = self.remove_whitespace(track_nr)
        if track_nr:
            return track_nr
        return None

    def get_track_title(self, trackContainer):
        title_div = trackContainer.cssselect('div.product_tracklist_heading_records_title[itemprop="name"]')
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
                return length
        return None


class Search(BaseSearch):

    _base_url = 'http://www.junodownload.com'
    url = 'http://www.junodownload.com/betasearch/'
    exception = JunodownloadAPIError

    def __unicode__(self):
        return u'<JunodownloadSearch: term="' + self.search_term + u'">'

    def get_params(self):
        return {'solrorder':'relevancy', 'submit-search':'SEARCH', 'q[all][]':self.search_term}

    def prepare_response_content(self, content):
        #get the raw response content and parse it
        self.parsed_response = lxml.html.document_fromstring(content)

    def get_release_containers(self):
        return self.parsed_response.cssselect('div.productlist_widget_product_detail')[:25]

    def get_release_name(self,releaseContainer):
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

    def get_release_info(self,releaseContainer):
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

    def get_release_instance(self,releaseContainer):
        release_anchor = releaseContainer.cssselect('div.productlist_widget_product_title span a')
        if len(release_anchor) != 1:
            self.raise_exception(u'could not find release link anchor')
        release_link = self._base_url + release_anchor[0].attrib['href']
        return Release.release_from_url(release_link)