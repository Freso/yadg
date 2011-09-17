# coding=utf-8
import requests,lxml.html,re
from django.utils.datastructures import SortedDict


READABLE_NAME = 'Musicbrainz'


class MusicBrainzAPIError(Exception):
    pass


class APIBase(object):
    
    _base_url = 'http://musicbrainz.org/'
    
    def __init__(self):
        self._cached_response = None
        self._url_appendix = None
        self._params = None
    
    @property
    def _response(self):
        if not self._cached_response:
            r = requests.get(self._base_url + self._url_appendix, params=self._params)
            if r.status_code == 200:
                self._cached_response = r
            else:
                raise MusicBrainzAPIError, '%d' % (404 if r.status_code == 400 else r.status_code)
        return self._cached_response
    
    def _remove_whitespace(self, string):
        return ' '.join(string.split())


class Release(APIBase):
    def __init__(self,id):
        APIBase.__init__(self)
        self.id = id
        self._url_appendix = 'release/%s' % id
        self._data = {}
        
    def _raise_exception(self,message):
        raise MusicBrainzAPIError, u'%s [%s]' % (message,self.id)
        
    def _extract_infos(self):
        data = {}
        
        #get the raw response content and parse it
        #we explicitely decode the response content to unicode
        content = self._response.content.decode('utf-8')
        doc = lxml.html.document_fromstring(content)
        
        sidebar_div = doc.cssselect('div#sidebar')
        if len(sidebar_div) != 1:
            self._raise_exception(u'could not find sidebar div')
        sidebar_div = sidebar_div[0]
        content_div = doc.cssselect('div#content')
        if len(content_div) != 1:
            self._raise_exception(u'could not find content div')
        content_div = content_div[0]
        
        sidebar_h2 = sidebar_div.cssselect('h2')
        
        for caption in sidebar_h2:
            if caption.text_content() in (u'Release information',u'Additional details'):
                dl = caption.getnext()
                children = dl.getchildren()
                if len(children) % 2 == 1:
                    self._raise_exception(u'Release information or Additional details dl has uneven number of children')
                while children:
                    dt = children[0].text_content()
                    dd = children[1].text_content()
                    children = children[2:]
                    if dt == 'Date:':
                        data['released'] = self._remove_whitespace(dd)
                    elif dt == 'Country:':
                        data['country'] = self._remove_whitespace(dd)
                    elif dt == 'Format:' and dd != '(unknown)':
                        if data.has_key('format'):
                            format = data['format'] + ', ' + self._remove_whitespace(dd)
                        else:
                            format = self._remove_whitespace(dd)
                        data['format'] = format
                    elif dt == 'Type:':
                        if data.has_key('format'):
                            format = data['format'] + ', ' + self._remove_whitespace(dd)
                        else:
                            format = self._remove_whitespace(dd)
                        data['format'] = format
            elif caption.text_content() == 'Labels':
                label_ul = caption.getnext()
                label_li = label_ul.cssselect('li')
                if len(label_li) != 0:
                    data['label'] = []
                for li in label_li:
                    spans = li.cssselect('span')
                    if len(spans) > 2 or len(spans) == 0:
                        self._raise_exception(u'could not get label and catalog# from list entry')
                    elif len(spans) == 1:
                        label_span = spans[0]
                        catalog_span = None
                    else:
                        (label_span,catalog_span) = spans
                    label_a = label_span.cssselect('a')
                    if len(label_a) != 1:
                        self._raise_exception(u'could not get label link from list')
                    label_a = label_a[0]
                    data['label'].append(self._remove_whitespace(label_a.text_content()))
                    if catalog_span is not None:
                        if not data.has_key('catalog'):
                            data['catalog'] = []
                        data['catalog'].append(self._remove_whitespace(catalog_span.text_content()))
        
        releaseheader_div = content_div.cssselect('div.releaseheader')
        if len(releaseheader_div) != 1:
            self._raise_exception(u'could not find releaseheader div')
        releaseheader_div = releaseheader_div[0]
        
        title_a = releaseheader_div.cssselect('h1 a')
        if len(title_a) != 1:
            self._raise_exception(u'could not find release title a')
        title_a = title_a[0]
        
        data['title'] = self._remove_whitespace(title_a.text_content())
        
        artist_links = releaseheader_div.cssselect('p.subheader > a')
        if len(artist_links) == 0:
            self._raise_exception(u'could not find artist a')
        
        data['artists'] = []
        for artist_a in artist_links:
            artist = self._remove_whitespace(artist_a.text_content())
            if artist == 'Various Artists':
                artist = u'Various'
            data['artists'].append(artist)
        
        content_h2 = content_div.cssselect('h2')
        for caption in content_h2:
            if caption.text_content() == 'Tracklist':
                tracklist_table = caption.getnext()
                disc_divs = tracklist_table.cssselect('tbody > div')
                if len(disc_divs) == 0:
                    self._raise_exception(u'could not find any disc tracklisting')
                data['discs'] = SortedDict()
                for disc_div in disc_divs:
                    caption_tr = disc_div.getprevious()
                    caption_a = caption_tr.cssselect('a')
                    if len(caption_a) != 1:
                        self._raise_exception(u'could not determine disc header')
                    caption_a = caption_a[0]
                    m = re.search('\d+',caption_a.text_content())
                    if not m:
                        self._raise_exception(u'could not determine disc number')
                    disc_number = int(m.group(0))
                    data['discs'][disc_number] = []
                    
                    track_rows = disc_div.cssselect('span > tr')
                    for track_row in track_rows:
                        columns = track_row.cssselect('td')
                        if len(columns) == 5:
                            (track_number_td,title_td,artist_td,rating_td,length_td) = columns
                        elif len(columns) == 4:
                            (track_number_td,title_td,rating_td,length_td) = columns
                            artist_td = None
                        else:
                            self._raise_exception(u'track row has not the right amount of columns')
                        
                        track_number_span = track_number_td.cssselect('span')
                        if len(track_number_span) != 1:
                            self._raise_exception(u'could not get tracknumber')
                        track_number_span = track_number_span[0]
                        track_number = self._remove_whitespace(track_number_span.text_content())
                        
                        title_a = title_td.cssselect('a')
                        if len(title_a) != 1:
                            self._raise_exception(u'could not get track title')
                        title_a = title_a[0]
                        track_title = self._remove_whitespace(title_a.text_content())
                        
                        if artist_td is not None:
                            track_artists = []
                            track_artist_links = artist_td.cssselect('a')
                            if len(track_artist_links) == 0:
                                self._raise_exception(u'could not get track artists')
                            for track_artist_a in track_artist_links:
                                track_artist = self._remove_whitespace(track_artist_a.text_content())
                                if track_artist == 'Various Artists':
                                    track_artist = u'Various'
                                if not track_artist in track_artists:
                                    track_artists.append(track_artist)
                        else:
                            track_artists = None
                        
                        length_span = length_td.cssselect('span')
                        if len(length_span) != 1:
                            self._raise_exception(u'could not get track length')
                        length_span = length_span[0]
                        track_length = self._remove_whitespace(length_span.text_content())
                        
                        data['discs'][disc_number].append((track_number,track_artists,track_title,track_length))
        
        return data
    
    @property
    def data(self):
        if not self._data:
            self._data = self._extract_infos()
        return self._data
    
    @staticmethod
    def id_from_string(string_id):
        return string_id
    
    @staticmethod
    def release_from_url(url):
        m = re.match('^http://(?:www\.)?musicbrainz.org/release/([^\/]+)$',url)
        if m:
            return Release(m.group(1))
        else:
            return None
    
    def __unicode__(self):
        return u'<MusicBrainzRelease: id="' + self.id + u'">'
    


class Search(APIBase):
    
    def __init__(self, term):
        APIBase.__init__(self)
        self._term = term
        self._url_appendix = 'search'
        self._params = {'type':'release', 'limit':'25', 'query':term}
        self._releases = []
    
    def _raise_exception(self,message):
        raise MusicBrainzAPIError, u'%s ["%s"]' % (message,self._term)
    
    def _extract_releases(self):
        releases = []
        
        #get the raw response content and parse it
        #we explicitely decode the response content to unicode
        content = self._response.content.decode('utf-8')
        doc = lxml.html.document_fromstring(content)
        
        result_table = doc.cssselect('div#content table.tbl')
        
        if len(result_table) != 1:
            #no results
            return releases
        
        result_table = result_table[0]
        
        result_rows = result_table.cssselect('tbody tr')
        
        for row in result_rows:
            (score_col,title_col,artist_col,track_count_col,country_col,language_col) = row.getchildren()
            #get release link
            title_a = title_col.cssselect('a')
            if len(title_a) != 1:
                self._raise_exception(u'could not determine release title')
            title_a = title_a[0]
            #get artist link
            artist_links = artist_col.cssselect('a')
            if len(artist_links) == 0:
                self._raise_exception(u'could not determine release artist')
            #get track count
            track_count = self._remove_whitespace(track_count_col.text_content())
            #get country
            country = self._remove_whitespace(country_col.text_content())
            #get release title
            title = self._remove_whitespace(title_a.text_content())
            #get release artist
            artists = []
            for artist_a in artist_links:
                artist = self._remove_whitespace(artist_a.text_content())
                if artist == u'Various Artists':
                    artist = u'Various'
                artists.append(artist)
            #get release object
            release = Release.release_from_url(title_a.attrib['href'])
            #compile info
            info = u''
            if country:
                info += u'Country: ' + country
                if track_count:
                    info += u'|'
            if track_count:
                info += track_count + u' Tracks'
            #compile release name
            name = u', '.join(artists) + u' \u2013 ' + title
            #add result to list
            releases.append({'name':name,'info':info,'release':release})
            
        return releases
    
    @property
    def releases(self):
        if not self._releases:
            self._releases = self._extract_releases()
        return self._releases
    
    def __unicode__(self):
        return u'<MusicBrainzSearch: term="' + self._term + u'">'