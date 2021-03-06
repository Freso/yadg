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

from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MaxLengthValidator
from django.db.models.signals import m2m_changed, post_delete, post_save, pre_delete
from django.db.models.query import Q
from django.db.models import Max

from .scraper.factory import SCRAPER_CHOICES


class PublicTemplateManager(models.Manager):

    def get_query_set(self):
        return super(PublicTemplateManager, self).get_query_set().filter(Q(is_default__exact=True) | Q(is_public__exact=True))


class Template(models.Model):

    owner = models.ForeignKey(User)
    name = models.CharField(max_length=40,
                            help_text='Enter the name of the template here.')
    template = models.TextField(validators=[MaxLengthValidator(8192)], blank=True, help_text='Enter the template code here.')
    is_public = models.BooleanField(default=False,
                                    help_text='Make this template public. Public templates can be used by all users that are subscribed to you.')
    is_default = models.BooleanField(default=False,
                                     help_text='Make this template a default. Default templates can be used by all registered users and users that are not logged in.')
    is_utility = models.BooleanField(default=False,
                                     help_text="Mark this template as a utility. Utility templates are only used as the basis for other templates and won't appear in the list of available templates for rendering a release directly.")
    dependencies = models.ManyToManyField('self', symmetrical=False, related_name='depending_set', blank=True,
                                          help_text='Choose which templates this template depends on. Chosen templates can be included or extended in your template code.')

    objects = models.Manager()
    public_templates = PublicTemplateManager()

    def __unicode__(self):
        return u'%s [%s]' % (self.name, self.owner.username)

    def visible_to_user(self, user, assume_subscription=False):
        if user is None:
            return self.is_default
        else:
            if assume_subscription:
                return self.is_default or self.owner_id == user.id or self.is_public
            else:
                return self.is_default or self.owner_id == user.id or (self.owner.subscriber_set.filter(subscriber__exact=user).exists() and self.is_public)

    @property
    def is_visible(self):
        return self.is_default or self.is_public

    def get_unique_name(self):
        return 'template_%d' % self.pk

    def depends_on(self):
        return u', '.join(map(unicode, self.dependencies.all()))

    def dependencies_set(self):
        res = set()
        for f in self.dependencies.all():
            res.add(f)
            res.update(f.dependencies_set())
        return res

    def cached_dependencies_set(self, prefetch_owner=False):
        res = set()
        l = DependencyClosure.objects.filter(descendant__exact=self, path_length__gt=0).values('ancestor_id').distinct()
        q = Template.objects.filter(id__in=l)
        if prefetch_owner:
            q = q.select_related('owner')
        for f in q:
            res.add(f)
        return res

    def max_dependency_height(self, include_descendants):
        aggregate = DependencyClosure.objects.filter(descendant__exact=self).aggregate(max_height=Max('path_length'))
        height = aggregate['max_height']
        if include_descendants:
            aggregate = DependencyClosure.objects.filter(ancestor__exact=self).aggregate(max_height=Max('path_length'))
            height += aggregate['max_height']
        return height

    def depending_templates_requiring_public(self):
        return self.depending_set.filter(~Q(owner_id__exact=self.owner_id) | Q(owner_id__exact=self.owner_id, is_public__exact=True))

    @staticmethod
    def circular_checker(parent, child):
        """
        Checks that the object is not an ancestor or a descendant,
        avoid self links
        """
        if parent == child:
            raise ValidationError('A template may not depend on itself.')
        if child in parent.dependencies_set():
            raise ValidationError('One of the dependencies has a dependency on this template.')

    @staticmethod
    def templates_for_user(user, with_utility=True, sort_by_name=False, prefetch_owner=False):
        if user is not None and user.is_authenticated():
            subscribed_to = user.subscribed_to.values('user_id').distinct()
            t = Template.objects.filter(Q(owner__in=subscribed_to, is_public__exact=True) | Q(owner__exact=user.pk) | Q(is_default__exact=True))
        else:
            t = Template.objects.filter(is_default__exact=True)
        if not with_utility:
            t = t.filter(is_utility__exact=False)
        if prefetch_owner:
            t = t.select_related('owner')
        if sort_by_name:
            t = t.extra(select={'lower_name': 'lower(name)'}).order_by('lower_name')
        return t

    class Meta:
        unique_together = ('owner', 'name')


class DependencyClosure(models.Model):

    descendant = models.ForeignKey(Template, related_name='closure_descendant')
    ancestor = models.ForeignKey(Template, related_name='closure_ancestor')
    path_length = models.IntegerField()
    count = models.IntegerField()

    class Meta:
        unique_together = ('descendant', 'ancestor', 'path_length')

    def __unicode__(self):
        return u'%s depends on %s over %d hops' % (self.descendant, self.ancestor, self.path_length)


def dependency_changed(sender, **kwargs):
    """
    This method for updating the dependency closures assumes that only the forward relation for the many-to-many field
    is ever modified, i.e. template.dependencies.add(other_template) and never other_template.depending_set.add(template)
    """
    action = kwargs['action']
    if action == 'post_add':
        instance = kwargs['instance']
        pk_set = kwargs['pk_set']
        # get all templates that depend on the we one that was modified and are at least one hop away (exclude the self
        # links)
        modified_instance_descendants = DependencyClosure.objects.filter(ancestor_id__exact=instance.pk, path_length__gt=0)
        for pk in pk_set:
            # for every added dependency and it's dependencies we add a new path from the modified instance
            current_pk_ancestors = DependencyClosure.objects.filter(descendant_id__exact=pk)
            for current_pk_ancestor in current_pk_ancestors:
                # old situation:   pk --> ... --> current_pk_ancestor
                #                     \         /
                #                     path_length
                #
                # new situation:   instance --> pk --> ... --> current_pk_ancestor
                #                           \               /
                #                            path_length + 1
                #
                # Note: every template automatically has the path:         pk --
                #                                                           ^   \  length = 0
                #                                                            \__/
                #       so the path    instance --> pk   with length 1
                #       will be added without the need for any special corner case handling
                try:
                    # see if we already have a path from instance to current_pk_ancestor with the expected length
                    path_to_ancestor = DependencyClosure.objects.get(descendant_id__exact=instance.pk, ancestor_id__exact=current_pk_ancestor.ancestor_id, path_length=current_pk_ancestor.path_length+1)
                except DependencyClosure.DoesNotExist:
                    # if we don't create one
                    path_to_ancestor = DependencyClosure.objects.create(descendant_id=instance.pk, ancestor_id=current_pk_ancestor.ancestor_id, path_length=current_pk_ancestor.path_length+1, count=current_pk_ancestor.count)
                else:
                    # otherwise increase the count to include the new paths
                    path_to_ancestor.count += current_pk_ancestor.count
                    path_to_ancestor.save()

                # now we have to add the new path to all descendants of the modified instance
                #
                #       modified_instance_descendant --> ... --> instance --> ... --> current_pk_ancestor
                #                                    \        /           \         /
                #                                 old_path_length         path_length
                #
                # so the new path from modified_instance_descendant to current_pk_ancestor has a length of
                # old_path_length + path_length
                for modified_instance_descendant in modified_instance_descendants:
                    try:
                        # so see if such a path already exists
                        path_from_descendant_to_ancestor = DependencyClosure.objects.get(descendant_id__exact=modified_instance_descendant.descendant_id, ancestor_id__exact=path_to_ancestor.ancestor_id, path_length=modified_instance_descendant.path_length+path_to_ancestor.path_length)
                    except DependencyClosure.DoesNotExist:
                        # if not we create one
                        DependencyClosure.objects.create(descendant_id=modified_instance_descendant.descendant_id, ancestor_id=path_to_ancestor.ancestor_id, path_length=modified_instance_descendant.path_length+path_to_ancestor.path_length, count=current_pk_ancestor.count*modified_instance_descendant.count)
                    else:
                        # otherwise increase the count to include the new paths
                        path_from_descendant_to_ancestor.count += current_pk_ancestor.count*modified_instance_descendant.count
                        path_from_descendant_to_ancestor.save()
    elif action == 'post_remove':
        instance = kwargs['instance']
        pk_set = kwargs['pk_set']
        # get all templates that depend on the we one that was modified and are at least one hop away (exclude the self
        # links)
        modified_instance_descendants = DependencyClosure.objects.filter(ancestor_id__exact=instance.pk, path_length__gt=0)
        for pk in pk_set:
            # for every removed dependency and it's dependencies we remove the path from the modified instance
            current_pk_ancestors = DependencyClosure.objects.filter(descendant_id__exact=pk)
            for current_pk_ancestor in current_pk_ancestors:
                try:
                    # this object should exist, if it does not there is a consistency problem
                    path_to_ancestor = DependencyClosure.objects.get(descendant_id__exact=instance.pk, ancestor_id__exact=current_pk_ancestor.ancestor_id, path_length=current_pk_ancestor.path_length+1)
                except DependencyClosure.DoesNotExist:
                    # consistency error in the database, we can't do anything so continue with next pk
                    continue

                if path_to_ancestor.count <= current_pk_ancestor.count:
                    # if the removed path was the only path, remove the closure from the database
                    path_to_ancestor.delete()
                else:
                    # otherwise decrease the count to reflect the removal of the path
                    path_to_ancestor.count -= current_pk_ancestor.count
                    path_to_ancestor.save()

                # new delete the removed path from all descendants of the modified instance
                for modified_instance_descendant in modified_instance_descendants:
                    try:
                        # again this should exist
                        path_from_descendant_to_ancestor = DependencyClosure.objects.get(descendant_id__exact=modified_instance_descendant.descendant_id, ancestor_id__exact=path_to_ancestor.ancestor_id, path_length=modified_instance_descendant.path_length+path_to_ancestor.path_length)
                    except DependencyClosure.DoesNotExist:
                        # consistency error in the database, we can't do anything so continue
                        continue

                    if path_from_descendant_to_ancestor.count <= current_pk_ancestor.count*modified_instance_descendant.count:
                        # if the removed path was the only path, remove the closure from the database
                        path_from_descendant_to_ancestor.delete()
                    else:
                        # otherwise decrease the count to reflect the removal of the path
                        path_from_descendant_to_ancestor.count -= current_pk_ancestor.count*modified_instance_descendant.count
                        path_from_descendant_to_ancestor.save()
    elif action == 'post_clear':
        instance = kwargs['instance']
        # get all real ancestors and descendants of the modified instance
        modified_instance_ancestors = DependencyClosure.objects.filter(descendant_id__exact=instance.pk, path_length__gt=0)
        modified_instance_descendants = DependencyClosure.objects.filter(ancestor_id__exact=instance.pk, path_length__gt=0)
        for modified_instance_ancestor in modified_instance_ancestors:
            # all paths to ancestors of the modified instance will be removed, so remove those paths also from the
            # descendants of the modified instance
            for modified_instance_descendant in modified_instance_descendants:
                try:
                    # again this should exist
                    path_from_descendant_to_ancestor = DependencyClosure.objects.get(descendant_id__exact=modified_instance_descendant.descendant_id, ancestor_id__exact=modified_instance_ancestor.ancestor_id, path_length=modified_instance_descendant.path_length+modified_instance_ancestor.path_length)
                except DependencyClosure.DoesNotExist:
                    # consistency error in the database, we can't do anything so continue
                    continue

                if path_from_descendant_to_ancestor.count <= modified_instance_ancestor.count*modified_instance_descendant.count:
                    # if the removed path was the only path, remove the closure from the database
                    path_from_descendant_to_ancestor.delete()
                else:
                    # otherwise decrease the count to reflect the removal of the path
                    path_from_descendant_to_ancestor.count -= modified_instance_ancestor.count*modified_instance_descendant.count
                    path_from_descendant_to_ancestor.save()
        # now delete all ancestors
        modified_instance_ancestors.delete()


def template_pre_delete(sender, **kwargs):
    instance = kwargs['instance']
    # get all real ancestors and descendants (including the modified instance) of the modified instance
    modified_instance_ancestors = DependencyClosure.objects.filter(descendant_id__exact=instance.pk)
    modified_instance_descendants = DependencyClosure.objects.filter(ancestor_id__exact=instance.pk, path_length__gt=0)
    for modified_instance_ancestor in modified_instance_ancestors:
        # all paths to ancestors of the modified instance will be removed, so remove those paths also from the
        # descendants of the modified instance
        for modified_instance_descendant in modified_instance_descendants:
            try:
                # again this should exist
                path_from_descendant_to_ancestor = DependencyClosure.objects.get(descendant_id__exact=modified_instance_descendant.descendant_id, ancestor_id__exact=modified_instance_ancestor.ancestor_id, path_length=modified_instance_descendant.path_length+modified_instance_ancestor.path_length)
            except DependencyClosure.DoesNotExist:
                # consistency error in the database, we can't do anything so continue
                continue

            if path_from_descendant_to_ancestor.count <= modified_instance_ancestor.count*modified_instance_descendant.count:
                # if the removed path was the only path, remove the closure from the database
                path_from_descendant_to_ancestor.delete()
            else:
                # otherwise decrease the count to reflect the removal of the path
                path_from_descendant_to_ancestor.count -= modified_instance_ancestor.count*modified_instance_descendant.count
                path_from_descendant_to_ancestor.save()
    # now delete all ancestors
    modified_instance_ancestors.delete()


def template_saved(sender, **kwargs):
    instance = kwargs['instance']
    created = kwargs['created']
    if created:
        DependencyClosure.objects.create(ancestor_id=instance.pk, descendant_id=instance.pk, count=1, path_length=0)
    elif not instance.is_visible:
        # the template might have been public before, so remove all dependencies that are not from templates
        # owned by this user and from public templates that are owned by the user
        dependant_templates = instance.depending_templates_requiring_public()
        for template in dependant_templates:
            # remove the modified instance from each template that does not belong to the owner
            template.dependencies.remove(instance)


m2m_changed.connect(dependency_changed, sender=Template.dependencies.through)
post_save.connect(template_saved, sender=Template)
pre_delete.connect(template_pre_delete, sender=Template)


class Subscription(models.Model):

    subscriber = models.ForeignKey(User, related_name='subscribed_to')
    user = models.ForeignKey(User, related_name='subscriber_set')

    class Meta:
        unique_together = ('user', 'subscriber')

    def __unicode__(self):
        return u'%s to %s' % (self.subscriber.username, self.user.username)

    def clean(self):
        # don't allow reflexive subscriptions
        if self.subscriber == self.user:
            raise ValidationError('Subscriptions to yourself are not allowed')


def subscription_deleted(sender, **kwargs):
    instance = kwargs['instance']
    l1 = Template.objects.filter(owner_id__exact=instance.subscriber_id)
    l2 = Template.objects.filter(owner_id__exact=instance.user_id, is_default__exact=False)
    for deps in Template.dependencies.through.objects.filter(from_template__in=l1, to_template__in=l2).select_related('from_template', 'to_template'):
        deps.from_template.dependencies.remove(deps.to_template)


post_delete.connect(subscription_deleted, sender=Subscription)


class Settings(models.Model):

    class Meta:
        verbose_name_plural = "settings"

    user = models.OneToOneField(User, null=True, blank=True,
                                help_text='The user these settings belong to. If left blank these settings will apply to every unauthenticated user')
    default_template = models.ForeignKey(Template, blank=True, null=True, on_delete=models.SET_NULL,
                                         help_text='This template will be the default template when viewing a result.')
    default_scraper = models.CharField(max_length=40, choices=SCRAPER_CHOICES, blank=True, null=True,
                                       help_text='This scraper will be selected by default in the scraper dropdown menu.')

    def __unicode__(self):
        if self.user:
            username = u"%s's" % self.user.username
        else:
            username = u'default'

        return username + u" settings"