# coding=utf-8
import requests,lxml.html,re
from django.utils.datastructures import SortedDict

READABLE_NAME = 'Discogs'

class DiscogsAPIError(Exception):
    pass


class APIBase(object):
    
    _base_url = 'http://www.discogs.com/'
    
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
                raise DiscogsAPIError, '%d' % r.status_code
        return self._cached_response
    
    def _remove_whitespace(self, string):
        return ' '.join(string.split())
    

class Release(APIBase):
    
    presuffixes = [
        (u'The ', u', The'),
        (u'A ', u', A'),
    ]
    
    def __init__(self, id):
        APIBase.__init__(self)
        self.id = id
        self._url_appendix = 'release/%d' % id
        self._data = {}
    
    def _swapsuffix(self, string):
        for (prefix,suffix) in self.presuffixes:
            if string.endswith(suffix):
                string = prefix + string[:-len(suffix)]
                #we assume there is only one suffix to swap
                break
        return string
            
    def _extract_infos(self):
        data = {}
        
        #get the raw response content and parse it
        #we explicitely decode the response content to unicode
        content = self._response.content.decode('utf-8')
        doc = lxml.html.document_fromstring(content)
        
        #get the div that contains all the information we want
        container = doc.cssselect('div#page > div.lr > div.left')
        if len(container) != 1:
            raise DiscogsAPIError, u'could not find anchor point'
        container = container[0]
        
        #get artist and title
        title_element = container.cssselect('div.profile h1')
        if len(title_element) != 1:
            raise DiscogsAPIError, u'could not find title element'
        artist_elements = title_element[0].cssselect('a')
        if len(artist_elements) == 0:
            raise DiscogsAPIError, u'could not find artist elements'
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
        
        discs = SortedDict()
        
        #get track listing
        tracklist_tables = container.cssselect('div#tracklist table')
        if not tracklist_tables:
            raise DiscogsAPIError, u'could not find tracklisting'
        for table in tracklist_tables:
            rows = table.cssselect('tr')
            if not rows:
                raise DiscogsAPIError, u'could not find track information'
            for row in rows:
                #ignore rows that don't have the right amount of columns
                if len(row.getchildren()) != 5:
                    continue
                (track_pos,track_artists_column,track,track_duration,filler) = row.getchildren()
                #determine cd and track number
                m = re.search('(?i)^(?:(?:(?:cd)?(\d{1,2})-)|(?:cd(?:\s+|\.|-)))?(\d+|(\w\d*))(?:\.)?$',track_pos.text_content())
                if not m:
                    #ignore tracks with strange track number
                    continue
                number = m.group(2)
                if not re.match('\w',number):
                    number = int(number)
                (track_cd_number,track_number) = (m.group(1),number)
                #if there is no cd number we default to 1
                if not track_cd_number:
                    track_cd_number = 1
                else:
                    track_cd_number = int(track_cd_number)
                #get track artist
                track_artists_elements = track_artists_column.cssselect('a')
                if track_artists_elements:
                    track_artists = []
                else:
                    track_artists = None
                for track_artist_element in track_artists_elements:
                    track_artist = track_artist_element.text_content()
                    track_artist = self._remove_whitespace(track_artist)
                    track_artist = self._swapsuffix(track_artist)
                    track_artists.append(track_artist)
                #get track title
                track_title = track.cssselect('span.track_title')
                if len(track_title) != 1:
                    raise DiscogsAPIError, u'could not determine track title'
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
        return u'<Release: id=%d>' % self.id

    
class Search(APIBase):
    
    def __init__(self, term):
        APIBase.__init__(self)
        self._term = term
        self._url_appendix = 'search'
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
            release_link = container.cssselect('div.data > div > a')
            if len(release_link) != 1:
                raise DiscogsAPIError, u'could not extract release link from:' + container.text
            release_link = release_link[0]
            
            #get additional info
            release_info = container.cssselect('div.data > div.search_release_stats')
            if len(release_info) != 1:
                raise DiscogsAPIError, u'could not extract additional info from: ' + container.text
            release_info = release_info[0].text_content()
            
            #get release name
            release_name = release_link.text_content()

            #get the release id
            m = re.search('/(release|master)/(\d+)$',release_link.attrib['href'])
            if not m:
                raise DiscogsAPIError, u'could not get release id from: ' + release_link.attrib['href']
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
        return u'<Search: term="' + self._term + u'">'