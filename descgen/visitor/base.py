#!/usr/bin/python
# -*- coding: utf-8 -*-


"""
taken from: http://peter-hoffmann.com/2010/extrinsic-visitor-pattern-python-inheritance.html
"""
class Visitor(object):
    def visit(self, obj, *args, **kwargs):
        meth = None
        for cls in obj.__class__.__mro__:
            meth_name = 'visit_'+cls.__name__
            meth = getattr(self, meth_name, None)
            if meth:
                break

        if not meth:
            meth = self.generic_visit
        return meth(obj, *args, **kwargs)

    def generic_visit(self, obj, *args, **kwargs):
        raise NotImplementedError()