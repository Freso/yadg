from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models.signals import m2m_changed, post_delete, post_save
from django.core.validators import RegexValidator
from django.db.models.query import Q


class Template(models.Model):

    owner = models.ForeignKey(User)
    name = models.CharField(max_length=30, validators=[RegexValidator(regex='^[A-Za-z0-9\(\)\[\]\-_ ]+$'),],
                            help_text='The name of the template. Only letters, numbers, hyphens and parenthesis are allowed.')
    template = models.TextField(max_length=8192, help_text='Enter the template code here.')
    is_public = models.BooleanField(default=False,
                                    help_text='Make this template public. Public templates can be used by all users that are subscribed to you.')
    is_default = models.BooleanField(default=False,
                                     help_text='Make this template a default. Default templates can be used by all registered users and users that are not logged in.')
    dependencies = models.ManyToManyField('self', symmetrical=False, related_name='depending_set', blank=True,
                                          help_text='Choose which templates this template depends on. Chosen templates can be included or extended in your template code.')

    def __unicode__(self):
        return u'%s-%s' % (self.owner.username, self.name)

    def get_unique_name(self):
        return '%s_%s' % (self.owner.username, self.name)

    def clean(self):
        pass

    def depends_on(self):
        return u', '.join(map(unicode, self.dependencies.all()))

    def dependencies_set(self):
        res = set()
        for f in self.dependencies.all():
            res.add(f)
            res.update(f.dependencies_set())
        return res

    def cached_dependencies_set(self):
        res = set()
        for f in DependencyClosure.objects.filter(descendant__exact=self).select_related('ancestor'):
            res.add(f.ancestor)
        return res

    # def descendants_set(self):
    #     res = set()
    #     for f in self.depending_set.all():
    #         res.add(f)
    #         res.update(f.descendants_set())
    #     return res

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
        # if child in parent.descendants_set():
        #     raise ValidationError('The object is a descendant.')

    @staticmethod
    def templates_for_user(user):
        if user.is_authenticated:
            subscribed_to = user.subscribed_to.values('user_id').distinct()
            return Template.objects.filter(Q(owner__in=subscribed_to, is_public__exact=True) | Q(owner__exact=user.pk) | Q(is_default__exact=True))
        else:
            return Template.objects.filter(is_default__exact=True)

    class Meta:
        unique_together = ('owner', 'name')


class DependencyClosure(models.Model):

    descendant = models.ForeignKey(Template, related_name='closure_descendant')
    ancestor = models.ForeignKey(Template, related_name='closure_ancestor')

    class Meta:
        unique_together = ('descendant', 'ancestor')

    def __unicode__(self):
        return u'%s depends on %s' % (self.descendant, self.ancestor)


def dependency_changed(sender, **kwargs):
    action = kwargs['action']
    if action == 'post_add':
        instance = kwargs['instance']
        pk_set = kwargs['pk_set']
        # get all templates that depend on the we one that was modified
        cur_closure_descendants = DependencyClosure.objects.filter(ancestor__exact=instance.pk)
        for pk in pk_set:
            # for every added dependency check if we already have an entry for that in the closure table
            if not DependencyClosure.objects.filter(descendant_id__exact=instance.pk, ancestor_id__exact=pk).exists():
                # this dependency has no entry in the closure table, so we create one
                new_dep = DependencyClosure.objects.create(descendant_id=instance.pk, ancestor_id=pk)
                # and update every descendant (= template that depends on this template)
                for cur_closure_descendant in cur_closure_descendants:
                    # check if the descendant already has a dependency for the newly added template dependency, if not create one
                    if not DependencyClosure.objects.filter(descendant_id__exact=cur_closure_descendant.descendant_id, ancestor_id__exact=new_dep.ancestor_id).exists():
                        DependencyClosure.objects.create(descendant_id=cur_closure_descendant.descendant_id, ancestor_id=new_dep.ancestor_id)
                # the added dependency could have dependencies itself, so add those to this template and any of its descendants
                new_closure_deps = DependencyClosure.objects.filter(descendant_id__exact=pk)
                for new_closure_dep in new_closure_deps:
                    modified_closure = None
                    # does the template already have a dependency for the dependency of the newly added one
                    if not DependencyClosure.objects.filter(descendant_id__exact=instance.pk, ancestor_id__exact=new_closure_dep.ancestor_id).exists():
                        # if it does not, create one
                        modified_closure = DependencyClosure.objects.create(descendant_id=instance.pk, ancestor_id=new_closure_dep.ancestor_id)
                    # and update all descendants again
                    if modified_closure is not None:
                        for cur_closure_descendant in cur_closure_descendants:
                            if not DependencyClosure.objects.filter(descendant_id__exact=cur_closure_descendant.descendant_id, ancestor_id__exact=modified_closure.ancestor_id).exists():
                                DependencyClosure.objects.create(descendant_id=cur_closure_descendant.descendant_id, ancestor_id=modified_closure.ancestor_id)
    elif action == 'post_remove':
        instance = kwargs['instance']
        pk_set = kwargs['pk_set']
        # get a list of all dependencies of the modified template
        l = DependencyClosure.objects.filter(descendant_id__exact=instance.pk).values_list('ancestor')
        deps_modified = False
        for pk in pk_set:
            # check if any of the other dependencies has a dependency to the removed template
            if not DependencyClosure.objects.filter(descendant_id__in=l, ancestor_id__exact=pk).exists():
                # if it does not the dependency is local to the modified template and has to be deleted
                DependencyClosure.objects.filter(descendant_id__exact=instance.pk, ancestor_id__exact=pk).delete()
                deps_modified = True
        # if we modified the dependencies we have to update all descendants
        if deps_modified:
            # for this we first get a list of all descendants
            l2 = DependencyClosure.objects.filter(ancestor_id__exact=instance.pk).values_list('descendant')
            # get a list of template objects that have to be updated (create a python list to force immediate evaluation
            # of the query
            templates = list(Template.objects.filter(pk__in=l2))
            # now delete all cached dependencies for the templates
            DependencyClosure.objects.filter(descendant_id__in=l2).delete()
            # create now closures by brute forcing the calculation for each template
            for template in templates:
                dependencies = template.dependencies_set()
                # create a new closure for each dependency
                for dependency in dependencies:
                    DependencyClosure.objects.create(descendant=template, ancestor=dependency)
    elif action == 'post_clear':
        instance = kwargs['instance']
        # delete all cached dependencies for the modified template
        DependencyClosure.objects.filter(descendant_id__exact=instance.pk).delete()
        # then get a list of descendant templates that need to be updated
        l = DependencyClosure.objects.filter(ancestor_id__exact=instance.pk).values_list('descendant')
        # get a list of template objects that have to be updated (create a python list to force immediate evaluation
        # of the query
        templates = list(Template.objects.filter(pk__in=l))
        # now delete all cached dependencies for the templates
        DependencyClosure.objects.filter(descendant_id__in=l).delete()
        # create now closures by brute forcing the calculation for each template
        for template in templates:
            dependencies = template.dependencies_set()
            # create a new closure for each dependency
            for dependency in dependencies:
                DependencyClosure.objects.create(descendant=template, ancestor=dependency)


def template_deleted(sender, **kwargs):
    instance = kwargs['instance']
    closure = DependencyClosure.objects.filter(descendant__exact=instance, ancestor__exact=instance)
    if closure.count() > 1:
        closure.delete()


def template_saved(sender, **kwargs):
    instance = kwargs['instance']
    if not (instance.is_default or instance.is_public):
        # the template might have been public before, so remove all dependencies that are not from templates
        # owned by this user
        dependant_templates = instance.depending_set.filter(~Q(owner_id__exact=instance.owner.pk))
        for template in dependant_templates:
            # remove the modified instance from each template that does not belong to the owner
            template.dependencies.remove(instance)


m2m_changed.connect(dependency_changed, sender=Template.dependencies.through)
post_delete.connect(template_deleted, sender=Template)
post_save.connect(template_saved, sender=Template)


class Subscription(models.Model):

    subscriber = models.ForeignKey(User, related_name='subscribed_to')
    user = models.ForeignKey(User, related_name='subscriber_set')

    class Meta:
        unique_together = ('user', 'subscriber')

    def __unicode__(self):
        return u'%s to %s' % (self.subscriber.username, self.user.username)

