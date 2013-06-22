#!/usr/bin/python
# -*- coding: utf-8 -*-


class Result(object):
    pass


class NotFoundResult(Result):
    pass


class ListResult(Result):

    class ListItem(object):

        name = None
        info = None
        query = None
        url = None

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

    items = []

    def create_item(self):
        return self.ListItem()

    def append_item(self, item):
        self.items.append(item)

    def get_items(self):
        return self.items


class ReleaseResult(Result):

    class ArtistTypes(object):

        MAIN = 2**0
        FEATURING = 2**1
        REMIXER = 2**2

    class ReleaseEvent(object):

        date = None
        country = None

        def set_date(self, date):
            self.date = date

        def set_country(self, country):
            self.country = country

        def get_date(self):
            return self.date

        def get_country(self):
            return self.country

    class LabelId(object):

        label = None
        catalogue_nr = []

        def set_label(self, label):
            self.label = label

        def append_catalogue_nr(self, catalogue_nr):
            self.catalogue_nr.append(catalogue_nr)

        def get_label(self):
            return self.label

        def get_catalogue_nrs(self):
            return self.catalogue_nr

    class Artist(object):

        name = None
        type = 0
        various = False

        def set_name(self, name):
            self.name = name

        def get_name(self):
            return self.name

        def set_type(self, type):
            self.type = type

        def add_type(self, type):
            self.type = self.type | type

        def has_type(self, type):
            return True if self.type & type > 0 else False

        def set_various(self, various):
            self.various = various

        def is_various(self):
            return self.various

    class Disc(object):

        class Track(object):

            number = None
            artists = []
            title = None
            length = None

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

        number = None
        title = None
        tracks = []

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

    release_events = []
    format = None
    label_ids = []
    title = None
    artists = []
    genres = []
    styles = []
    url = None
    discs = []

    def create_release_event(self):
        return self.ReleaseEvent()

    def append_release_event(self, release_event):
        self.release_events.append(release_event)

    def get_release_events(self):
        return self.release_events

    def set_format(self, format):
        self.format = format

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

    def get_artists(self):
        return self.artists

    def add_genre(self, genre):
        self.genres.append(genre)

    def get_genres(self):
        return self.genres

    def add_style(self, style):
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