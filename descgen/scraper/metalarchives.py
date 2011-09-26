# coding=utf-8
import lxml.html,re,json
from descgen.scraper.base import APIBase


READABLE_NAME = 'Metal-Archives'


class MetalarchivesAPIError(Exception):
    pass


class MetalarchivesAPIBase(APIBase):
    
    _base_url = 'http://www.metal-archives.com/'
    _exception = MetalarchivesAPIError


class Release(MetalarchivesAPIBase):
    
    def __init__(self, id):
        MetalarchivesAPIBase.__init__(self)
        self.id = id
        self._url_appendix = '/albums///%d' % id
        self._object_id = str(id)
        self._data = {}

    def _get_link(self,release_artist='',release_name=''):
        return 'http://www.metal-archives.com/albums/%s/%s/%d' %(release_artist,release_name,self.id)
        
    def _extract_infos(self):
        data = {}
        
        #get the raw response content and parse it
        #we explicitely decode the response content to unicode
        content = self._response.content.decode('utf-8')
        doc = lxml.html.document_fromstring(content)
        
        #stupid website doesn't send correct http status code
        h3_404 = doc.cssselect('h3')
        for candidate in h3_404:
            if candidate.text_content() == 'Error 404':
                raise self._exception, u'404'
        
        title_h1 = doc.cssselect('div#album_info h1.album_name')
        if len(title_h1) != 1:
            self._raise_exception(u'could not find album title h1')
        title_h1 = title_h1[0]
        
        data['title'] = self._remove_whitespace(title_h1.text_content())
        
        artists_h2 = doc.cssselect('div#album_info h2.band_name')
        if len(artists_h2) == 0:
            self._raise_exception(u'could not find artist h2')
        artists = []
        for artist_h2 in artists_h2:
            artists.append(self._remove_whitespace(artist_h2.text_content()))
        
        data['artists'] = artists
        
        data['title'] = self._remove_whitespace(title_h1.text_content())
        
        info_dl = doc.cssselect('div#album_info dl')
        for dl in info_dl:
            children = dl.getchildren()
            if len(children) % 2 == 1:
                self._raise_exception(u'album info dl has uneven number of children')
            while children:
                dt = children[0].text_content()
                dd = self._remove_whitespace(children[1].text_content())
                children = children[2:]
                if dt =='Type:':
                    data['format'] = dd
                elif dt == 'Release date:':
                    data['released'] = dd
                elif dt =='Label:':
                    data['label'] = [dd,]
        
        tracklist_table = doc.cssselect('div#album_tabs_tracklist table.table_lyrics tbody')
        if len(tracklist_table) != 1:
            self._raise_exception(u'could not find tracklist table')
        tracklist_table = tracklist_table[0]
        table_rows = tracklist_table.cssselect('tr')
        discs = {}
        disc_number = 1
        for row in table_rows:
            columns = row.cssselect('td')
            if len(columns) == 1:
                header = columns[0].text_content()
                m = re.match('(?:Disc|CD) (\d+)',header)
                if m:
                    disc_number = int(m.group(1))
            elif len(columns) == 4:
                (track_number_td,track_title_td,track_length_td,lyrics_td) = columns
                
                m = re.search('(\d+)(?:\.)?',track_number_td.text_content())
                if m:
                    track_number = m.group(1)
                else:
                    self._raise_exception(u'could not extract track number')
                    
                track_title = self._remove_whitespace(track_title_td.text_content())
                
                track_length = self._remove_whitespace(track_length_td.text_content())
                
                if not discs.has_key(disc_number):
                    discs[disc_number] = []
                
                discs[disc_number].append((track_number,None,track_title,track_length))
            else:
                continue
        
        data['discs'] = discs
        
        data['link'] = self._get_link()
        
        return data
    
    @property
    def data(self):
        if not self._data:
            self._data = self._extract_infos()
        return self._data
    
    @staticmethod
    def release_from_url(url):
        m = re.match('^http://(?:www\.)?metal-archives\.com/albums/(?:.*?/){0,2}(\d+)$',url)
        if m:
            return Release(int(m.group(1)))
        else:
            return None
    
    @staticmethod
    def id_from_string(string_id):
        m = re.search('\D',string_id)
        if m:
            raise ValueError
        id = int(string_id)
        return id
    
    def __unicode__(self):
        return u'<MetalarchivesRelease: id=%d>' % self.id


class Search(MetalarchivesAPIBase):
    
    def __init__(self, term):
        MetalarchivesAPIBase.__init__(self)
        self._term = term
        self._url_appendix = 'search/ajax-album-search/'
        self._object_id = u'"' + term + u'"'
        self._params = {'field':'title', 'query':term}
        self._releases = []
    
    def _extract_releases(self):
        releases = []
        
        content = self._response.content
        try:
            response = json.loads(content)
        except:
            self._raise_exception(u'invalid server response')
        
        if (response.has_key('aaData') and len(response['aaData']) == 0) or not response.has_key('aaData'):
            return releases
        
        for entry in response['aaData'][:25]:
            (artists_html,title_html,type,date_html) = entry
            
            artists_div = lxml.html.fragment_fromstring(artists_html, create_parent="div")
            title_div = lxml.html.fragment_fromstring(title_html, create_parent="div")
            date_div = lxml.html.fragment_fromstring(date_html, create_parent="div")
            
            date = date_div.text_content()
            date = self._remove_whitespace(date)
            
            artists_a = artists_div.cssselect('a')
            if len(artists_a) == 0:
                self._raise_exception(u'could not extract artists')
            artists = []
            for artist_a in artists_a:
                artists.append(self._remove_whitespace(artist_a.text_content()))
                
            title_a = title_div.cssselect('a')
            if len(title_a) != 1:
                self._raise_exception(u'could not extract release title')
            title_a = title_a[0]
            
            title = title_a.text_content()
            
            release = Release.release_from_url(title_a.attrib['href'])
            
            info_components = filter(lambda x: x, [date,type])
            
            info = u'|'.join(info_components)
            
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
        return u'<MetalarchivesSearch: term="' + self._term + u'">'