#!/usr/bin/python
# -*- coding: utf-8 -*-

from .base import Visitor
from ..formatter import Formatter


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
