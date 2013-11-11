from django.db import models
from django.contrib.auth.models import User


class Template(models.Model):

    template = models.TextField(max_length=8192)
    is_public = models.BooleanField(default=False)
    is_default = models.BooleanField(default=False)
    dependencies = models.ManyToManyField('self', symmetrical=False, related_name='depending_set')
    users = models.ManyToManyField(User, through='Subscription')

    def __unicode__(self):
        return self.name + ' (%d)' % self.pk

    def get_unique_name(self):
        return (u'%d-' % self.pk) + self.name

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.is_public and self.dependencies.filter(is_public__exact=False).count() > 0:
            raise ValidationError('A template may only be public if all of its dependencies are public.')


class Subscription(models.Model):

    user = models.ForeignKey(User)
    template = models.ForeignKey(Template)
    name = models.CharField(max_length=30)
    is_owner = models.BooleanField(default=False)

    class Meta:
        unique_together = (('user', 'template'), ('user', 'name'))