#!/usr/bin/python
# -*- coding: utf-8 -*-

from .base import Visitor
from ..result import ReleaseResult


class SerializeVisitor(Visitor):

    ARTIST_TYPE_TRANSLATION = {
        ReleaseResult.ArtistTypes.MAIN: "ArtistTypes.MAIN",
        ReleaseResult.ArtistTypes.FEATURING: "ArtistTypes.FEATURING",
        ReleaseResult.ArtistTypes.REMIXER: "ArtistTypes.REMIXER"
    }

    ALBUM_ART_TYPE_TRANSLATION = {
        ReleaseResult.AlbumArtTypes.BACK: "AlbumArtTypes.BACK",
        ReleaseResult.AlbumArtTypes.DISC: "AlbumArtTypes.DISC",
        ReleaseResult.AlbumArtTypes.FRONT: "AlbumArtTypes.FRONT",
        ReleaseResult.AlbumArtTypes.INLET: "AlbumArtTypes.INLET"
    }

    def __init__(self, var_name):
        self.var_name = var_name

    def _serialize_artists(self, artists, var_name, track_var_name=None, empty_line=True):
        code = []
        for artist in artists:
            code.append(u'%s = %s.create_artist()' % (var_name, self.var_name))
            code.append(u'%s.set_name(%r)' % (var_name, artist.get_name()))
            code.append(u'%s.set_various(%r)' % (var_name, artist.is_various()))
            for artist_type in artist.get_types():
                code.append(u'%s.append_type(%s.%s)' % (var_name, self.var_name, self.ARTIST_TYPE_TRANSLATION[artist_type]))
            if track_var_name:
                code.append(u'%s.append_artist(%s)' % (track_var_name, var_name))
            else:
                code.append(u'%s.append_release_artist(%s)' % (self.var_name, var_name))
            if empty_line:
                code.append(u'')
        return code

    def visit_NotFoundResult(self, result):
        code = []
        code.append(u'%s = NotFoundResult()' % self.var_name)
        code.append(u'%s.set_scraper_name(%r)' % (self.var_name, result.get_scraper_name()))
        return u'\n'.join(code)

    def visit_ListResult(self, result):
        code = []
        code.append(u'%s = ListResult()' % self.var_name)
        code.append(u'%s.set_scraper_name(%r)' % (self.var_name, result.get_scraper_name()))
        for item in result.get_items():
            code.append('')
            code.append(u'item = %s.create_item()' % self.var_name)
            code.append(u'item.set_name(%r)' % item.get_name())
            code.append(u'item.set_info(%r)' % item.get_info())
            code.append(u'item.set_query(%r)' % item.get_query())
            code.append(u'item.set_url(%r)' % item.get_url())
            code.append(u'%s.append_item(item)' % self.var_name)
        return u'\n'.join(code)

    def visit_ReleaseResult(self, result):
        code = []
        code.append(u'%s = ReleaseResult()' % self.var_name)
        code.append(u'%s.set_scraper_name(%r)' % (self.var_name, result.get_scraper_name()))
        code.append(u'')
        for release_event in result.get_release_events():
            code.append(u'release_event = %s.create_release_event()' % self.var_name)
            code.append(u'release_event.set_date(%r)' % release_event.get_date())
            code.append(u'release_event.set_country(%r)' % release_event.get_country())
            code.append(u'%s.append_release_event(release_event)' % self.var_name)
            code.append(u'')
        code.append(u'%s.set_format(%r)' % (self.var_name, result.get_format()))
        code.append(u'')
        for label_id in result.get_label_ids():
            code.append(u'label_id = %s.create_label_id()' % self.var_name)
            code.append(u'label_id.set_label(%r)' % label_id.get_label())
            for catalogue_nr in label_id.get_catalogue_nrs():
                code.append(u'label_id.append_catalogue_nr(%r)' % catalogue_nr)
            code.append(u'%s.append_label_id(label_id)' % self.var_name)
            code.append(u'')
        code.append(u'%s.set_title(%r)' % (self.var_name, result.get_title()))
        code.append(u'')
        code.extend(self._serialize_artists(result.get_release_artists(), u'artist'))
        for genre in result.get_genres():
            code.append(u'%s.append_genre(%r)' % (self.var_name, genre))
        code.append(u'')
        for style in result.get_styles():
            code.append(u'%s.append_style(%r)' % (self.var_name, style))
        code.append(u'')
        code.append(u'%s.set_url(%r)' % (self.var_name, result.get_url()))
        code.append(u'')
        for disc in result.get_discs():
            code.append(u'disc = %s.create_disc()' % self.var_name)
            code.append(u'disc.set_number(%r)' % disc.get_number())
            code.append(u'disc.set_title(%r)' % disc.get_title())
            code.append(u'')
            for track in disc.get_tracks():
                code.append(u'track = disc.create_track()')
                code.append(u'track.set_number(%r)' % track.get_number())
                code.append(u'track.set_title(%r)' % track.get_title())
                code.append(u'track.set_length(%r)' % track.get_length())
                code.extend(self._serialize_artists(track.get_artists(), u'track_artist', u'track', False))
                code.append(u'disc.append_track(track)')
                code.append(u'')
            code.append(u'%s.append_disc(disc)' % self.var_name)
            code.append(u'')
        for album_art in result.get_album_arts():
            code.append(u'album_art = %s.create_album_art()' % self.var_name)
            code.append(u'album_art.set_url(%r)' % album_art.get_url())
            code.append(u'album_art.set_type(%s.%s)' % (self.var_name, self.ALBUM_ART_TYPE_TRANSLATION[album_art.get_type()]))
            code.append(u'album_art.set_width(%r)' % album_art.get_width())
            code.append(u'album_art.set_height(%r)' % album_art.get_height())
            code.append(u'album_art.set_hint(%r)' % album_art.geT_hint())
            code.append(u'%s.append_album_art(album_art)' % self.var_name)
            code.append(u'')
        return u'\n'.join(code)


class JSONSerializeVisitor(Visitor):

    RESULT_TYPE_NAME = u'type'

    ALBUM_ART_TYPE_TRANSLATION = {
        ReleaseResult.AlbumArtTypes.BACK: u'back',
        ReleaseResult.AlbumArtTypes.DISC: u'disc',
        ReleaseResult.AlbumArtTypes.FRONT: u'front',
        ReleaseResult.AlbumArtTypes.INLET: u'inlet'
    }

    ARTIST_TYPE_TRANSLATION = {
        ReleaseResult.ArtistTypes.MAIN: u'main',
        ReleaseResult.ArtistTypes.FEATURING: u'guest',
        ReleaseResult.ArtistTypes.REMIXER: u'remixer'
    }

    def _unicode_or_none(self, str):
        if str is not None:
            return unicode(str)
        else:
            return None

    def visit_NotFoundResult(self, result):
        out = {
            self.RESULT_TYPE_NAME: u'NotFoundResult'
        }
        return out

    def visit_ListItem(self, item):
        out = {
            u'name':  self._unicode_or_none(item.get_name()),
            u'info':  self._unicode_or_none(item.get_info()),
            u'query': self._unicode_or_none(item.get_query()),
            u'url':   self._unicode_or_none(item.get_url())
        }
        return out

    def visit_ListResult(self, result):
        out = {
            self.RESULT_TYPE_NAME: u'ListResult',

            u'items': map(lambda x: self.visit(x), result.get_items())
        }
        return out

    def visit_AlbumArt(self, albumart):
        out = {
            u'url':    self._unicode_or_none(albumart.get_url()),
            u'type':   self.ALBUM_ART_TYPE_TRANSLATION[albumart.get_type()] if albumart.get_type() else None,
            u'width':  albumart.get_width(),
            u'height': albumart.get_height(),
            u'hint':   self._unicode_or_none(albumart.get_hint())
        }
        return out

    def visit_ReleaseEvent(self, rel_event):
        out = {
            u'date':    self._unicode_or_none(rel_event.get_date()),
            u'country': self._unicode_or_none(rel_event.get_country())
        }
        return out

    def visit_LabelId(self, labelId):
        out = {
            u'label':        self._unicode_or_none(labelId.get_label()),
            u'catalogueNrs': map(lambda x: self._unicode_or_none(x), labelId.get_catalogue_nrs())
        }
        return out

    def visit_Artist(self, artist):
        out = {
            u'name':      self._unicode_or_none(artist.get_name()),
            u'types':     map(lambda x: self.ARTIST_TYPE_TRANSLATION[x], artist.get_types()),
            u'isVarious': artist.is_various()
        }
        return out

    def visit_Track(self, track):
        out = {
            u'number':  self._unicode_or_none(track.get_number()),
            u'artists': map(lambda x: self.visit(x), track.get_artists()),
            u'title':   self._unicode_or_none(track.get_title()),
            u'length':  track.get_length()
        }
        return out

    def visit_Disc(self, disc):
        out = {
            u'number': disc.get_number(),
            u'title':  disc.get_title(),
            u'tracks': map(lambda x: self.visit(x), disc.get_tracks())
        }
        return out

    def visit_ReleaseResult(self, result):
        out = {
            self.RESULT_TYPE_NAME: u'ReleaseResult',

            u'releaseEvents': map(lambda x: self.visit(x), result.get_release_events()),
            u'format':        self._unicode_or_none(result.get_format()),
            u'labelIds':      map(lambda x: self.visit(x), result.get_label_ids()),
            u'title':         self._unicode_or_none(result.get_title()),
            u'artists':       map(lambda x: self.visit(x), result.get_release_artists()),
            u'genres':        map(lambda x: self._unicode_or_none(x), result.get_genres()),
            u'styles':        map(lambda x: self._unicode_or_none(x), result.get_styles()),
            u'url':           self._unicode_or_none(result.get_url()),
            u'discs':         map(lambda x: self.visit(x), result.get_discs()),
            u'albumArts':     map(lambda x: self.visit(x), result.get_album_arts())
        }
        return out


class CheckReleaseResultVisitor(Visitor):

    def visit_ReleaseResult(self, result):
        return True

    def generic_visit(self, obj, *args, **kwargs):
        return False