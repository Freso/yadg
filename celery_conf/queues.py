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

from kombu import Exchange, Queue
from descgen.scraper.factory import ScraperFactory
from os.path import commonprefix


class Factory(object):

    scraper_factory = ScraperFactory()
    default_exchange = 'default'
    default_queue = 'default'
    default_routing_key = 'default'

    def __init__(self):
        self.queues = None
        self.class_routing_keys = {}
        self.queue_rate_limits = {}
        self._populate_queues()

    def _populate_queues(self):
        if self.queues is None:
            # the default queue (without any rate limit) which will be used for all scrapers that are not part of an
            # explicit rate limit group
            self.queues = [
                Queue(self.default_queue, Exchange(self.default_exchange, type='direct'), routing_key=self.default_routing_key)
            ]
            self.queue_rate_limits[self.default_queue] = None

            queue_names = {}
            rate_limit_groups = self.scraper_factory.get_rate_limit_groups()
            for rate_limit_group in rate_limit_groups:
                # get the complete class paths of all scraper objects in the rate limit group
                class_paths = map(lambda x: x.__module__ + '.' + x.__name__, rate_limit_group.get_objects())

                # extract the longest common prefix of these class paths, strip dots at the end and take it as base for
                # the queue name
                longest_prefix = commonprefix(class_paths)
                orig_name = longest_prefix.rstrip('.')

                # make sure queue names are unique
                name = orig_name
                i = 1
                while name in queue_names:
                    name = orig_name + '.' + str(i)
                    i += 1
                queue_names[name] = True

                # we take the (unique) queue name as its routing key also
                routing_key = name

                # save the routing key for all class paths in this rate limit group (for use by the router later)
                for class_path in class_paths:
                    self.class_routing_keys[class_path] = routing_key

                # save the given rate limit for the queue
                self.queue_rate_limits[name] = rate_limit_group.get_rate_limit()

                # finally create the queue and save it in the list
                queue = Queue(name, Exchange(self.default_exchange, type='direct'), routing_key=routing_key)
                self.queues.append(queue)

    def get_default_queue(self):
        return self.default_queue

    def get_default_routing_key(self):
        return self.default_routing_key

    def get_queues(self):
        return self.queues

    def get_class_routing_keys(self):
        return self.class_routing_keys

    def get_queue_rate_limits(self):
        return self.queue_rate_limits
