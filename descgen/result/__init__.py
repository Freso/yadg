#!/usr/bin/python
# -*- coding: utf-8 -*-


#There are several classes in this module that were supposed to be inner classes of their result class. Those classes
#were moved to the module level to allow pickling of the result classes which is necessary for celery


class CommonEqualityAndReprMixin(object):

    def __repr__(self):
        return "<%s: %r>" % (self.__class__.__name__, self.__dict__)

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self.__eq__(other)


class Result(CommonEqualityAndReprMixin):

    def __init__(self):
        self.scraper_name = None

    def set_scraper_name(self, scraper_name):
        self.scraper_name = scraper_name

    def get_scraper_name(self):
        return self.scraper_name


class NotFoundResult(Result):
    pass


class ListItem(CommonEqualityAndReprMixin):

    def __init__(self):
        super(ListItem, self).__init__()
        self.name = None
        self.info = None
        self.query = None
        self.url = None

    def set_name(self, name):
        self.name = name

    def set_info(self, info):
        self.info = info

    def set_query(self, query):
        self.query = query

    def get_name(self):
        return self.name

    def get_info(self):
        return self.info

    def get_query(self):
        return self.query

    def set_url(self, url):
        self.url = url

    def get_url(self):
        return self.url


class ListResult(Result):

    ListItem = ListItem

    def __init__(self):
        super(ListResult, self).__init__()
        self.items = []

    def create_item(self):
        return self.ListItem()

    def append_item(self, item):
        self.items.append(item)

    def get_items(self):
        return self.items


class ArtistTypes(object):

    MAIN = 2**0
    FEATURING = 2**1
    REMIXER = 2**2


class AlbumArtTypes(object):

    FRONT = 2**0
    BACK = 2**1
    DISC = 2**2
    INLET = 2**3


class AlbumArt(CommonEqualityAndReprMixin):

    def __init__(self):
        super(AlbumArt, self).__init__()
        self.url = None
        self.type = None
        self.width = None
        self.height = None
        self.hint = None

    def set_url(self, url):
        self.url = url

    def set_type(self, art_type):
        self.type = art_type

    def set_width(self, width):
        self.width = width

    def set_height(self, height):
        self.height = height

    def set_hint(self, hint):
        self.hint = hint

    def get_url(self):
        return self.url

    def get_type(self):
        return self.type

    def get_width(self):
        return self.width

    def get_height(self):
        return self.height

    def get_hint(self):
        return self.hint


class ReleaseEvent(CommonEqualityAndReprMixin):

    def __init__(self):
        super(ReleaseEvent, self).__init__()
        self.date = None
        self.country = None

    def set_date(self, date):
        self.date = date

    def set_country(self, country):
        self.country = country

    def get_date(self):
        return self.date

    def get_country(self):
        return self.country


class LabelId(CommonEqualityAndReprMixin):

    def __init__(self):
        super(LabelId, self).__init__()
        self.label = None
        self.catalogue_nrs = []

    def set_label(self, label):
        self.label = label

    def append_catalogue_nr(self, catalogue_nr):
        self.catalogue_nrs.append(catalogue_nr)

    def get_label(self):
        return self.label

    def get_catalogue_nrs(self):
        return self.catalogue_nrs


class Artist(CommonEqualityAndReprMixin):

    def __init__(self):
        super(Artist, self).__init__()
        self.name = None
        self.types = []
        self.various = False

    def set_name(self, name):
        self.name = name

    def get_name(self):
        return self.name

    def append_type(self, artist_type):
        self.types.append(artist_type)

    def get_types(self):
        return self.types

    def set_various(self, various):
        self.various = various

    def is_various(self):
        return self.various


class Track(CommonEqualityAndReprMixin):

    def __init__(self):
        super(Track, self).__init__()
        self.number = None
        self.artists = []
        self.title = None
        self.length = None

    def set_number(self, number):
        self.number = number

    def get_number(self):
        return self.number

    def append_artist(self, artist):
        self.artists.append(artist)

    def get_artists(self):
        return self.artists

    def set_title(self, title):
        self.title = title

    def get_title(self):
        return self.title

    def set_length(self, length):
        self.length = length

    def get_length(self):
        return self.length


class Disc(CommonEqualityAndReprMixin):

    Track = Track

    def __init__(self):
        super(Disc, self).__init__()
        self.number = None
        self.title = None
        self.tracks = []

    def set_number(self, number):
        self.number = number

    def get_number(self):
        return self.number

    def set_title(self, title):
        self.title = title

    def get_title(self):
        return self.title

    def create_track(self):
        return self.Track()

    def append_track(self, track):
        self.tracks.append(track)

    def get_tracks(self):
        return self.tracks


class ReleaseResult(Result):

    ArtistTypes = ArtistTypes
    AlbumArtTypes = AlbumArtTypes
    AlbumArt = AlbumArt
    ReleaseEvent = ReleaseEvent
    LabelId = LabelId
    Artist = Artist
    Disc = Disc

    def __init__(self):
        super(ReleaseResult, self).__init__()
        self.release_events = []
        self.format = None
        self.label_ids = []
        self.title = None
        self.artists = []
        self.genres = []
        self.styles = []
        self.url = None
        self.discs = []
        self.album_arts = []

    def create_release_event(self):
        return self.ReleaseEvent()

    def append_release_event(self, release_event):
        self.release_events.append(release_event)

    def get_release_events(self):
        return self.release_events

    def set_format(self, release_format):
        self.format = release_format

    def get_format(self):
        return self.format

    def create_label_id(self):
        return self.LabelId()

    def append_label_id(self, label_id):
        self.label_ids.append(label_id)

    def get_label_ids(self):
        return self.label_ids

    def set_title(self, title):
        self.title = title

    def get_title(self):
        return self.title

    def create_artist(self):
        return self.Artist()

    def append_release_artist(self, artist):
        self.artists.append(artist)

    def get_release_artists(self):
        return self.artists

    def append_genre(self, genre):
        self.genres.append(genre)

    def get_genres(self):
        return self.genres

    def append_style(self, style):
        self.styles.append(style)

    def get_styles(self):
        return self.styles

    def set_url(self, url):
        self.url = url

    def get_url(self):
        return self.url

    def create_disc(self):
        return self.Disc()

    def append_disc(self, disc):
        self.discs.append(disc)

    def get_discs(self):
        return self.discs

    def create_album_art(self):
        return self.AlbumArt()

    def append_album_art(self, album_art):
        self.album_arts.append(album_art)

    def get_album_arts(self):
        return self.album_arts
