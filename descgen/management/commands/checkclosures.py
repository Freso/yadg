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

from django.core.management.base import BaseCommand
from ...models import Template
import sys


def cmp_func(x, y):
    return cmp(x.name.lower(), y.name.lower())


class Command(BaseCommand):
    help = 'Checks if the cached dependency closures equate the actual dependencies.'

    def handle(self, *args, **options):
        count = Template.objects.all().count()
        i = 0
        last = 0
        clean = True
        for template in Template.objects.all():
            cached = template.cached_dependencies_set()
            actual = template.dependencies_set()

            if cached != actual:
                self.stdout.write('Mismatch for template "%s" (%d):\n' % (template.name, template.pk))
                self.stdout.write('  is:\n')
                if cached:
                    for templ in sorted(cached, cmp_func):
                        self.stdout.write('    * %s (%d)\n' % (templ.name, templ.pk))
                else:
                    self.stdout.write('    <empty>\n')
                self.stdout.write('  should be:\n')
                if actual:
                    for templ in sorted(actual, cmp_func):
                        self.stdout.write('    * %s (%d)\n' % (templ.name, templ.pk))
                else:
                    self.stdout.write('    <empty>\n')
                self.stdout.write('\n\n')
                clean = False

            i += 1
            percent = (i / float(count))*100
            if percent >= last+5:
                last = (percent // 5) * 5
                sys.stderr.write('%d%%\n' % last)


        if clean:
            self.stdout.write('No discrepancies detected.')
        else:
            self.stdout.write('There were discrepancies.')
            sys.exit(1)