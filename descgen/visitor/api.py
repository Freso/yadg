#!/usr/bin/python
# -*- coding: utf-8 -*-

from .base import Visitor
from django.core.urlresolvers import reverse
from django.utils.http import urlencode
from ..result import ReleaseResult
from ..formatter import Formatter

import urllib2


class APIVisitorV1(Visitor):

    ARTIST_TYPE_TRANSLATION = {
        ReleaseResult.ArtistTypes.MAIN: "Main",
        ReleaseResult.ArtistTypes.FEATURING: "Feature",
        ReleaseResult.ArtistTypes.REMIXER: "Remixer"
    }

    ARTIST_NAME_VARIOUS = 'Various'

    def __init__(self, description_format, include_raw_data):
        self.description_format = description_format
        self.include_raw_data = include_raw_data
        self.formatter = Formatter()

    def _convert_artists(self, artists):
        result = []
        for artist in artists:
            if ReleaseResult.ArtistTypes.MAIN in artist.get_types():
                artist_type = self.ARTIST_TYPE_TRANSLATION[ReleaseResult.ArtistTypes.MAIN]
            else:
                artist_type = self.ARTIST_TYPE_TRANSLATION[artist.get_types()[0]]
            if artist.is_various():
                name = self.ARTIST_NAME_VARIOUS
            else:
                name = artist.get_name()
            result.append({
                "name": name,
                "type": artist_type
            })
        return result

    def visit_NotFoundResult(self, result):
        data = {
            "type": "release_not_found"
        }
        return data

    def visit_ListResult(self, result):
        scraper_name = result.get_scraper_name()
        data = {
            "release_count": len(result.get_items()),
            "releases": {},
            "type": "release_list"
        }
        if result.get_items():
            data['releases'][scraper_name] = []
        for item in result.get_items():
            data["releases"][scraper_name].append({
                "name": item.get_name(),
                "info": item.get_info(),
                "release_url": item.get_url(),
                "query_url": urllib2.unquote(reverse('api_v1_makequery')) + '?' + urlencode({'input': item.get_query()})
            })
        return data

    def visit_ReleaseResult(self, result):
        format = self.formatter.get_valid_format(self.description_format)
        data = {
            "type": "release",
            "description_format": format,
            "description": self.formatter.description_from_ReleaseResult(result, format)
        }

        if self.include_raw_data:
            raw_data = {}

            for release_event in result.get_release_events():
                if release_event.get_date():
                    raw_data['released'] = release_event.get_date()
                if release_event.get_country():
                    raw_data['country'] = release_event.get_country()
                break

            release_format = result.get_format()
            if release_format:
                raw_data['format'] = release_format

            labels = []
            catalogue_nrs = []
            for label_id in result.get_label_ids():
                if label_id.get_label():
                    labels.append(label_id.get_label())
                for catalogue_nr in label_id.get_catalogue_nrs():
                    catalogue_nrs.append(catalogue_nr)
                    break
            if labels:
                raw_data['label'] = labels
            if catalogue_nrs:
                raw_data['catalog'] = catalogue_nrs

            title = result.get_title()
            if title:
                raw_data['title'] = title

            artists = self._convert_artists(result.get_release_artists())
            if artists:
                raw_data['artists'] = artists

            genres = result.get_genres()
            if genres:
                raw_data['genre'] = genres

            styles = result.get_styles()
            if styles:
                raw_data['style'] = styles

            url = result.get_url()
            if url:
                raw_data['link'] = url

            discs = {}
            disc_titles = {}
            if result.get_discs():
                max_digits = len(str(max(map(lambda disc: disc.get_number(), result.get_discs()))))
            for disc in result.get_discs():
                disc_number = disc.get_number()
                disc_number = 'disc_' + str(disc_number).zfill(max_digits)
                discs[disc_number] = []
                title = disc.get_title()
                if title:
                    disc_titles[disc_number] = title
                for track in disc.get_tracks():
                    track_number = track.get_number()
                    track_artists = self._convert_artists(track.get_artists())
                    track_title = track.get_title()
                    if track.get_length():
                        track_length = '%02d:%02d' % divmod(track.get_length(), 60)
                    else:
                        track_length = None

                    discs[disc_number].append([track_number, track_artists, track_title, track_length])
            if discs:
                raw_data['discs'] = discs
            if disc_titles:
                raw_data['discTitles'] = disc_titles

            data["raw_data"] = raw_data

        return data
