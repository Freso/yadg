# coding=utf-8
import lxml.html
from base import BaseRelease, BaseSearch, BaseAPIError


READABLE_NAME = 'Junodownload'


class JunodownloadAPIError(BaseAPIError):
    pass


class Release(BaseRelease):
    pass


class Search(BaseSearch):
    pass