#!/usr/bin/python
# -*- coding: utf-8 -*-
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