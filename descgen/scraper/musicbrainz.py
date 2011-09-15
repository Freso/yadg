# coding=utf-8
import musicbrainz2.webservice as ws
import musicbrainz2.utils as u


READABLE_NAME = 'Musicbrainz'


class MusicBrainzAPIError(Exception):
    pass


class Release(object):
    def __init__(self,id):
        self.id = id
        self._data = {}
        
    @property
    def data(self):
        if not self._data:
            q = ws.Query()
            include = ws.ReleaseIncludes(artist=True, tracks=True, discs=True, labels=True, tags=True, releaseGroup=True)
            try:
                release = q.getReleaseById(self.id,include)
            except (ws.ResourceNotFoundError,ws.RequestError):
                raise MusicBrainzAPIError, u'404'
            except Exception as e:
                raise MusicBrainzAPIError, unicode(e)
            self._data['title'] = release.getTitle()
            if release.getArtist():
                self._data['artist'] = [release.getArtist().getName(),]
            else:
                self._data['artist'] = [u'Various',]
            disc_track_counts = map(lambda x: len(x.getTracks()), release.getDiscs())
            self._data['discs'] = {}
            for disc_number in range(len(disc_track_counts)):
                self._data['discs'][disc_number+1] = []
        return self._data
    
    @staticmethod
    def release_from_url(url):
        #m = re.match('^http://(?:www\.)?discogs\.com/(?:.+?/)?release/(\d+)',url)
        #if m:
        #    return Release(int(m.group(1)))
        #else:
            return None