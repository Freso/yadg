# coding=utf-8
import lxml.html,re
from descgen.scraper.base import APIBase

READABLE_NAME = 'Discogs'

class DiscogsAPIError(Exception):
    pass


class DiscogsAPIBase(APIBase):
    
    _base_url = 'http://www.discogs.com/'
    _exception = DiscogsAPIError
    

class Release(DiscogsAPIBase):
    
    presuffixes = [
        (u'The ', u', The'),
        (u'A ', u', A'),
    ]
    
    def __init__(self, id):
        DiscogsAPIBase.__init__(self)
        self.id = id
        self._url_appendix = 'release/%d' % id
        self._object_id = str(id)
        self._data = {}
    
    def _swapsuffix(self, string):
        for (prefix,suffix) in self.presuffixes:
            if string.endswith(suffix):
                string = prefix + string[:-len(suffix)]
                #we assume there is only one suffix to swap
                break
        return string
            
            
    def _get_link(self):
        return self._base_url + self._url_appendix
            
    def _extract_infos(self):
        data = {}
        
        #get the raw response content and parse it
        #we explicitely decode the response content to unicode
        content = self._response.content.decode('utf-8')
        doc = lxml.html.document_fromstring(content)
        
        #get the div that contains all the information we want
        container = doc.cssselect('div#page > div.lr > div.left')
        if len(container) != 1:
            self._raise_exception(u'could not find anchor point')
        container = container[0]
        
        #get artist and title
        title_element = container.cssselect('div.profile h1')
        if len(title_element) != 1:
            self._raise_exception(u'could not find title element')
        artist_elements = title_element[0].cssselect('a')
        if len(artist_elements) == 0:
            self._raise_exception(u'could not find artist elements')
        artists = []
        for artist_element in artist_elements:
            artist = artist_element.text_content()
            artist = self._remove_whitespace(artist)
            artist = self._swapsuffix(artist)
            artists.append(artist)
        title = self._remove_whitespace(title_element[0].text_content())
        #right now this contains 'artist - title', so remove 'artist'
        title = title.split(u' \u2013 ')[1]
        
        data['artists'] = artists
        data['title'] = title
        
        #get additional infos
        additional_infos = container.cssselect('div.head + div.content')
        for additional_info in additional_infos:
            label_element = additional_info.getprevious()
            #get label and remove whitespace and ':'
            label = label_element.text_content()
            label = self._remove_whitespace(label)
            #make sure only valid keys are present
            label = re.sub('\W','',label)
            label = label.lower()
            #get content and remove whitespace
            content = additional_info.text_content()
            content = self._remove_whitespace(content)
            if label in ('genre','style','label','catalog'):
                content = content.split(',')
                #remove leading and trailing whitespace
                content = map(lambda x: x.rstrip().lstrip(),content)
                #remove empty elements
                content = filter(lambda x: x, content)
            if label == 'label':
                #sometimes we have the format "label - catalog#" for a label
                labels = []
                catalog_nr = []
                for c in content:
                    #split label and catalog#
                    split = c.split(u' \u2013 ')
                    if len(split) == 2: #we have exactely label and catalog#
                        labels.append(split[0])
                        if split[1] != 'none': #the catalog# should not be 'none'
                            catalog_nr.append(split[1])
                    else:
                        #we just have a label or to many components, so don't change anything
                        labels.append(c)
                #if there is not an explicit catalog# already, we add them to the data dict
                if not data.has_key('catalog') and catalog_nr:
                    data['catalog'] = catalog_nr
                #add the updated data to the dict
                content = labels
            if content and (content != 'none'):
                data[label] = content
        
        discs = {}
        
        #get track listing
        tracklist_tables = container.cssselect('div#tracklist table')
        if not tracklist_tables:
            self._raise_exception(u'could not find tracklisting')
        for table in tracklist_tables:
            rows = table.cssselect('tr')
            if not rows:
                self._raise_exception(u'could not find track information')
            for row in rows:
                #ignore rows that don't have the right amount of columns
                if len(row.getchildren()) != 5:
                    continue
                (track_pos,track_artists_column,track,track_duration,filler) = row.getchildren()
                #determine cd and track number
                m = re.search('(?i)^(?:(?:(?:cd)?(\d{1,2})(?:-|\.|:))|(?:cd(?:\s+|\.|-)))?(\d+|(\w\d*))(?:\.)?$',track_pos.text_content())
                if not m:
                    #ignore tracks with strange track number
                    continue
                number = m.group(2)
                if not re.search('\D',number):
                    #remove leading zeros
                    number_without_zeros = number.lstrip('0')
                    #see if there is anything left
                    if number_without_zeros:
                        number = number_without_zeros
                    else:
                        #number consists only of zeros
                        number = '0'
                (track_cd_number,track_number) = (m.group(1),number)
                #if there is no cd number we default to 1
                if not track_cd_number:
                    track_cd_number = 1
                else:
                    track_cd_number = int(track_cd_number)
                #get track artist
                track_artists_elements = track_artists_column.cssselect('a')
                track_artists = []
                for track_artist_element in track_artists_elements:
                    track_artist = track_artist_element.text_content()
                    track_artist = self._remove_whitespace(track_artist)
                    track_artist = self._swapsuffix(track_artist)
                    track_artists.append(track_artist)
                #get track title
                track_title = track.cssselect('span.track_title')
                if len(track_title) != 1:
                    self._raise_exception(u'could not determine track title')
                track_title = track_title[0].text_content()
                track_title = self._remove_whitespace(track_title)
                #get track duration
                track_duration = track_duration.text_content()
                track_duration = self._remove_whitespace(track_duration)
                
                #insert the data into the dict
                if not discs.has_key(track_cd_number):
                    discs[track_cd_number] = []
                discs[track_cd_number].append((track_number,track_artists,track_title,track_duration))
        
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
        m = re.match('^http://(?:www\.)?discogs\.com/(?:.+?/)?release/(\d+)',url)
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
        return u'<DiscogsRelease: id=%d>' % self.id

    
class Search(DiscogsAPIBase):
    
    def __init__(self, term):
        DiscogsAPIBase.__init__(self)
        self._term = term
        self._url_appendix = 'search'
        self._object_id = u'"' + term + u'"'
        self._params = {'type':'releases', 'q':term}
        self._releases = []
        
    def _extract_releases(self):
        releases = []
        
        #get the raw response content and parse it
        #we explicitely decode the response content to unicode
        content = self._response.content.decode('utf-8')
        doc = lxml.html.document_fromstring(content)
        
        result_containers = doc.cssselect('div.search_result')
        
        for container in result_containers:
            #get the link containing the release
            release_link = container.cssselect('div.data > div:first-child > a')
            if len(release_link) != 1:
                self._raise_exception(u'could not extract release link from:' + container.text_content())
            release_link = release_link[0]
            
            #get additional info
            release_info = container.cssselect('div.data > div.search_release_stats')
            if len(release_info) != 1:
                self._raise_exception(u'could not extract additional info from: ' + container.text_content())
            release_info = release_info[0].text_content()
            
            #get release name
            release_name = release_link.text_content()

            #get the release id
            m = re.search('/(release|master)/(\d+)$',release_link.attrib['href'])
            if not m:
                self._raise_exception(u'could not get release id from: ' + release_link.attrib['href'])
            release_id = int(m.group(2))
            #check if current release is a master release
            master_release = (m.group(1) == 'master')
            
            #only append non master releases to the results
            if not master_release:
                releases.append({'name':release_name,'info':release_info,'release':Release(release_id)})
            
        return releases
    
    @property
    def releases(self):
        if not self._releases:
            self._releases = self._extract_releases()
        return self._releases
    
    def __unicode__(self):
        return u'<DiscogsSearch: term="' + self._term + u'">'