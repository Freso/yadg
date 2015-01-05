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

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from celery_conf.routers import Router
import os


class Command(BaseCommand):
    args = '<celery multi mode> <host_name> <pid_file_path> <log_file_path>'
    help = 'Returns a list of shell commands needed to start the necessary Celery worker nodes and setting the ' \
           'defined rate limits.'

    celery_app_path = 'celery_conf:app'

    def handle(self, *args, **options):
        if len(args) != 4:
            raise CommandError('incorrect number of arguments')

        mode = args[0].lower()
        if not mode in ['start', 'stop', 'restart']:
            raise CommandError('invalid celery multi mode: %s' % mode)

        hostname = args[1]
        pid_file_path = os.path.join(args[2], '%N.pid')
        log_file_path = os.path.join(args[3], '%N.log')

        queue_factory = settings.CELERY_QUEUE_FACTORY
        task_name = Router.task_name

        queue_count = len(queue_factory.get_queues())

        start_command = 'celery multi %s %d -A %s -l info --hostname=%s --pidfile=%s --logfile=%s' % (mode, queue_count, self.celery_app_path, hostname, pid_file_path, log_file_path)
        rate_limit_commands = []
        queue_rate_limits = queue_factory.get_queue_rate_limits()

        i = 1
        for queue in queue_factory.get_queues():
            rate_limit = queue_rate_limits.get(queue.name, None)
            start_command += ' -Q:%d %s' %(i, queue.name)
            if rate_limit is not None:
                rate_limit_commands.append('celery -A %s control -d celery%d@%s rate_limit %s %s' % (self.celery_app_path, i, hostname, task_name, rate_limit))
            i += 1

        print start_command

        if rate_limit_commands and mode in ['start', 'restart']:
            print
            for command in rate_limit_commands:
                print command