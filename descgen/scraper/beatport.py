# coding=utf-8
import json,re,requests


READABLE_NAME = 'Beatport'


class BeatportAPIError(Exception):
    pass


class APIBase(object):
    
    _base_url = 'http://api.beatport.com/'
    
    def __init__(self):
        self._cached_response = None
        self._url_appendix = None
        self._params = None
    
    @property
    def _response(self):
        if not self._cached_response:
            r = requests.get(self._base_url + self._url_appendix, params=self._params)
            if r.status_code == 200:
                try:
                    self._cached_response = json.loads(r.content)
                except:
                    raise BeatportAPIError, u'invalid server response'
            else:
                raise BeatportAPIError, '%d' % r.status_code
        return self._cached_response
    
    def _remove_whitespace(self, string):
        return ' '.join(string.split())


class Release(APIBase):
    
    def __init__(self, id):
        APIBase.__init__(self)
        self.id = id
        self._url_appendix = 'catalog/releases/detail'
        self._params = {'format':'json','v':'1.0','id':id}
        self._data = {}
            
    def _raise_exception(self,message):
        raise BeatportAPIError, u'%s [%s]' % (message,self.id)
    
    def _extract_infos(self):
        data = {}
        
        if self._response['metadata']['count'] != 1:
            self._raise_exception(u'got more than one release for given id')
        
        release = self._response['results']
        
        if release.has_key('releaseDate'):
            data['released'] = release['releaseDate']
            
        if release.has_key('category') and release['category'] != 'Uncategorized':
            data['format'] = release['category']
        
        if release.has_key('label'):
            data['label'] = [release['label']['name'],]
        
        if release.has_key('catalogNumber'):
            data['catalog'] = [release['catalogNumber'],]
        
        if release.has_key('name'):
            data['title'] = release['name']
        
        if release.has_key('artists'):
            artists = []
            for artist_candidate in release['artists']:
                if artist_candidate['type'] == 'Artist':
                    artists.append(artist_candidate['name'])
            data['artists'] = artists
        
        if release.has_key('tracks'):
            data['discs'] = {"1":[]}
            track_number = 0
            for track in release['tracks']:
                track_number += 1
                track_number_str = str(track_number)
                if track.has_key('artists'):
                    track_artists = []
                    for track_artist_candidate in track['artists']:
                        if track_artist_candidate['type'] == 'Artist':
                            track_artists.append(track_artist_candidate['name'])
                    if track_artists == artists:
                        track_artists = None
                else:
                    track_artists = None
                if track.has_key('name'):
                    track_title = track['name']
                else:
                    track_title = ''
                if track.has_key('mixName') and track['mixName'] != 'Original Mix':
                    track_title += u' [' + self._remove_whitespace(track['mixName']) + u']'
                if track.has_key('length'):
                    track_length = track['length']
                else:
                    track_length = ''
                data['discs']["1"].append((track_number_str,track_artists,track_title,track_length))
        
        if release.has_key('genres'):
            data['genre'] = map(lambda x: x['name'], release['genres'])
        
        return data
    
    @property
    def data(self):
        if not self._data:
            self._data = self._extract_infos()
        return self._data
    
    @staticmethod
    def release_from_url(url):
        m = re.match('^http://(?:www\.)?beatport\.com/release/(?:.+?/)?(\d+)',url)
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
        return u'<BeatportRelease: id=%d>' % self.id

    
class Search(APIBase):
    
    def __init__(self, term):
        APIBase.__init__(self)
        self._term = term
        self._url_appendix = 'catalog/search'
        self._params = {'v':'2.0','format':'json','perPage':'25','page':'1','facets':['fieldType:release',], 'highlight':'false', 'query':term}
        self._releases = []
    
    def _raise_exception(self,message):
        raise BeatportAPIError, u'%s [%s]' % (message,self.term)
    
    def _extract_releases(self):
        releases = []
        
        if self._response.has_key('results'):
            for result in self._response['results']:
                if not result.has_key('id'):
                    continue
                id = result['id']
                release = Release(id)
                name_components = []
                if result.has_key('artists'):
                    artists = []
                    for artist in result['artists']:
                        if artist['type'] == 'Artist':
                            artists.append(artist['name'])
                    if artists:
                        name_components.append(u', '.join(artists))
                if result.has_key('name'):
                    name_components.append(result['name'])
                name = u' \u2013 '.join(name_components)
                add_info = []
                if result.has_key('releaseDate'):
                    add_info.append(result['releaseDate'])
                if result.has_key('label'):
                    add_info.append(result['label']['name'])
                if result.has_key('catalogNumber'):
                    add_info.append(result['catalogNumber'])
                info = u'|'.join(add_info)
                releases.append({'name':name,'info':info,'release':release})
            
        return releases
    
    @property
    def releases(self):
        if not self._releases:
            self._releases = self._extract_releases()
        return self._releases
    
    def __unicode__(self):
        return u'<BeatportSearch: term="' + self._term + u'">'