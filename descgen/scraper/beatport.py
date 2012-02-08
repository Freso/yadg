# coding=utf-8
import json,re
from base import APIBase


READABLE_NAME = 'Beatport'


class BeatportAPIError(Exception):
    pass


class BeatportAPIBase(APIBase):
    
    _base_url = 'http://api.beatport.com/'
    _exception = BeatportAPIError


class Release(BeatportAPIBase):
    
    def __init__(self, id):
        BeatportAPIBase.__init__(self)
        self.id = id
        self._url_appendix = 'catalog/releases/detail'
        self._object_id = str(id)
        self._params = {'format':'json','v':'1.0','id':id}
        self._data = {}
        self.release_url = self._get_link()

    def _get_link(self,release_name=''):
        return 'http://www.beatport.com/release/%s/%d' %(release_name,self.id)
        
    def _extract_infos(self):
        data = {}
        
        content = self._response.content
        try:
            response = json.loads(content)
        except:
            self._raise_exception(u'invalid server response')
        
        if response['metadata']['count'] != 1:
            self._raise_exception(u'got more than one release for given id')
        
        release = response['results']
        
        if release.has_key('releaseDate'):
            data['released'] = release['releaseDate']
            
        if release.has_key('category') and not release['category'] in ('Release','Uncategorized'):
            data['format'] = release['category']
        
        if release.has_key('label'):
            data['label'] = [release['label']['name'],]
        
        if release.has_key('catalogNumber'):
            data['catalog'] = [release['catalogNumber'],]
        
        if release.has_key('name'):
            data['title'] = release['name']
        
        if release.has_key('artists'):
            #get all real 'Artists' (not 'Remixers', etc.)
            real_artists = []
            for artist in release['artists']:
                if artist['type'] == 'Artist' and artist['name']:
                    real_artists.append({'name':artist['name'],'type':'Main'})
            #we assume that it is a Various Artists release if the release type is 'Album'
            #and the number of 'Artists' (not 'Remixers') is greater 1
            if release.has_key('category') and release['category'] == 'Album' and len(real_artists) > 1:
                artists = [{'name':'Various','type':'Main'},]
            else:
                artists = real_artists
            data['artists'] = artists
        
        if release.has_key('tracks'):
            data['discs'] = {1:[]}
            track_number = 0
            for track in release['tracks']:
                track_number += 1
                track_number_str = str(track_number)
                track_artists = []
                if track.has_key('artists'):
                    track_main_artists = []
                    track_additional_artists = []
                    for track_artist_candidate in track['artists']:
                        if track_artist_candidate['name']:
                            if track_artist_candidate['type'] == 'Artist':
                                track_main_artists.append({'name':track_artist_candidate['name'],'type':'Main'})
                            elif track_artist_candidate['type'] == 'Remixer':
                                track_additional_artists.append({'name':track_artist_candidate['name'],'type':'Remixer'})
                    if track_main_artists == artists:
                        track_artists = track_additional_artists
                    else:
                        track_artists = track_main_artists + track_additional_artists
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
                data['discs'][1].append((track_number_str,track_artists,track_title,track_length))
        
        if release.has_key('genres'):
            data['genre'] = map(lambda x: x['name'], release['genres'])
        
        data['link'] = self.release_url
        
        return data
    
    @property
    def data(self):
        if not self._data:
            self._data = self._extract_infos()
        return self._data
    
    @staticmethod
    def release_from_url(url):
        m = re.match('^http://(?:www\.)?beatport\.com/release/(?:.*?/)?(\d+)$',url)
        if m:
            release = Release(int(m.group(1)))
            release.release_url = url
            return release
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

    
class Search(BeatportAPIBase):
    
    def __init__(self, term):
        BeatportAPIBase.__init__(self)
        self._term = term
        self._url_appendix = 'catalog/search'
        self._object_id = u'"' + term + u'"'
        self._params = {'v':'2.0','format':'json','perPage':'25','page':'1','facets':['fieldType:release',], 'highlight':'false', 'query':term}
        self._releases = []
    
    def _extract_releases(self):
        releases = []
        
        content = self._response.content
        try:
            response = json.loads(content)
        except:
            self._raise_exception(u'invalid server response')
        
        if response.has_key('results'):
            for result in response['results']:
                if not result.has_key('id'):
                    continue
                id = result['id']
                release = Release(id)
                name_components = []
                if result.has_key('artists'):
                    #get all real 'Artists' (not 'Remixers', etc.)
                    real_artists = []
                    for artist in result['artists']:
                        if artist['type'] == 'Artist' and artist['name']:
                            real_artists.append(artist['name'])
                    #we assume that it is a Various Artists release if the release type is 'Album'
                    #and the number of 'Artists' (not 'Remixers') is greater 1
                    if result.has_key('category') and result['category'] == 'Album' and len(real_artists) > 1:
                        artists = ['Various',]
                    else:
                        artists = real_artists
                        
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
                info = u' | '.join(add_info)
                releases.append({'name':name,'info':info,'release':release})
            
        return releases
    
    @property
    def releases(self):
        if not self._releases:
            self._releases = self._extract_releases()
        return self._releases
    
    def __unicode__(self):
        return u'<BeatportSearch: term="' + self._term + u'">'