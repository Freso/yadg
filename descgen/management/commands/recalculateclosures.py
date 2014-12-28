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
from ...models import Template, DependencyClosure


class Command(BaseCommand):
    help = 'Recalculates all dependency closures.'

    def handle(self, *args, **options):
        # delete all existing closures
        self.stdout.write('Deleting all exisiting closures... ')
        DependencyClosure.objects.all().delete()
        self.stdout.write('done.\n\n')

        templates = Template.objects.all()
        templates_count = len(templates)
        descendants = {}
        ancestors = {}
        leaves = []

        self.stdout.write('Building dependency graph... ')
        i = 0
        last = 0
        # save the ancestors and descendants of each template in modifiable lists
        for template in templates:
            dl = descendants.setdefault(template.pk, [])
            for t in template.depending_set.all():
                dl.append(t)
            al = ancestors.setdefault(template.pk, [])
            for t in template.dependencies.all():
                al.append(t)
            # if the template has no ancestors it is a leaf
            if len(al) == 0:
                leaves.append(template)

            i += 1
            percent = (i / float(templates_count))*100
            if percent >= last+5:
                last = (percent // 5) * 5
                print '%d%%' % last
        self.stdout.write('done.\n\n')

        self.stdout.write('Creating dependency closures... ')
        i = 0
        last = 0
        while leaves:
            leaf = leaves[0]
            # create the reflexive closure
            DependencyClosure.objects.create(ancestor_id=leaf.pk, descendant_id=leaf.pk, count=1, path_length=0)
            # get all existing dependency paths originating from this leaf
            leaf_closures = DependencyClosure.objects.filter(descendant_id=leaf.pk)
            leaf_descendants = descendants[leaf.pk]
            while leaf_descendants:
                # for every descendant of this leaf
                descendant = leaf_descendants[0]
                for leaf_closure in leaf_closures:
                    # and every path originating from this leaf
                    try:
                        c = DependencyClosure.objects.get(descendant_id=descendant.pk, ancestor_id=leaf_closure.ancestor_id, path_length=leaf_closure.path_length+1)
                    except DependencyClosure.DoesNotExist:
                        # add a new path from the descendant to the ancestor of the path
                        DependencyClosure.objects.create(descendant_id=descendant.pk, ancestor_id=leaf_closure.ancestor_id, path_length=leaf_closure.path_length+1, count=leaf_closure.count)
                    else:
                        # or adjust the count of the existing path to reflect the newly added paths
                        c.count += leaf_closure.count
                        c.save()
                # remove the edge from descendant to leaf
                leaf_descendants.remove(descendant)
                ancestors[descendant.pk].remove(leaf)
                # if the descendant has no more ancestors it becomes a leaf
                if len(ancestors[descendant.pk]) == 0:
                    leaves.append(descendant)
            leaves = leaves[1:]

            i += 1
            percent = (i / float(templates_count))*100
            if percent >= last+5:
                last = (percent // 5) * 5
                print '%d%%' % last
        self.stdout.write('done.\n')