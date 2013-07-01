#!/usr/bin/python
# -*- coding: utf-8 -*-

from .base import Visitor
from ..formatter import Formatter
from ..result import ReleaseResult


class DescriptionVisitor(Visitor):

    class WrongResultType(Exception):
        pass

    def __init__(self, description_format):
        self.description_format = description_format
        self.formatter = Formatter()

    def visit_ReleaseResult(self, result):
        format = self.formatter.get_valid_format(self.description_format)

        return self.formatter.description_from_ReleaseResult(result, format)

    def generic_visit(self, obj, *args, **kwargs):
        raise self.WrongResultType(obj.__class__.__name__)


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