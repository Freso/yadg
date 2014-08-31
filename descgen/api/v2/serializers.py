#!/usr/bin/python
# -*- coding: utf-8 -*-
from rest_framework import serializers
from ...models import Template
from ...scraper.factory import SCRAPER_CHOICES, SCRAPER_DEFAULT
from ...mixins import CreateTaskMixin
from ...visitor.misc import JSONSerializeVisitor


class DependencyListingField(serializers.Field):
    def to_native(self, value):
        result = {}
        for val in value.all():
            result[val.get_unique_name()] = val.template
        return result


class TemplateSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.Field(source='pk')
    owner = serializers.Field(source='owner.username')
    code = serializers.Field(source='template')
    ownedByYou = serializers.SerializerMethodField('is_owner')
    default = serializers.SerializerMethodField('is_default')
    dependencies = DependencyListingField(source='dependencies')
    isUtility = serializers.Field(source='is_utility')

    class Meta:
        model = Template
        view_name = 'api_v2_template-detail'
        fields = ('url', 'id', 'owner', 'ownedByYou', 'name', 'code', 'isUtility', 'default', 'dependencies')

    def is_owner(self, obj):
        return obj.owner_id == self.context['request'].user.pk

    def is_default(self, obj):
        return obj == self.context['default_template']


class InputSerializer(serializers.Serializer, CreateTaskMixin):
    input = serializers.CharField(max_length=255, label='Search term')
    scraper = serializers.ChoiceField(required=False, choices=SCRAPER_CHOICES, default=SCRAPER_DEFAULT, label='Scraper')

    def save_object(self, obj, **kwargs):
        pass


class ApiSerializeVisitor(JSONSerializeVisitor):

    def visit_ListItem(self, item):
        out = super(ApiSerializeVisitor, self).visit_ListItem(item)
        out['queryParams'] = {'input': out['query'], 'scraper': ''}
        del out['query']
        return out