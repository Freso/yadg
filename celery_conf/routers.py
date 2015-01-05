#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2011-2015 Slack
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


class Router(object):

    task_name = 'descgen.tasks.get_result'

    def __init__(self, queue_factory):
        self.queue_factory = queue_factory
        self.class_routing_keys = queue_factory.get_class_routing_keys()

    def route_for_task(self, task, args=None, kwargs=None):
        # only handle get_result tasks
        if task == self.task_name:
            # that have the right amount of args
            if len(args) == 2:
                # if the given scraper has an explicit routing_key, use it
                class_path = args[0].__module__ + '.' + args[0].__class__.__name__
                if class_path in self.class_routing_keys:
                    return {
                        'queue': self.class_routing_keys[class_path],
                        'routing_key': self.class_routing_keys[class_path]
                    }
        return None