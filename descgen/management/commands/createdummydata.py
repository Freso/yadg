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
from django.contrib.auth.models import User
from ...models import Template, Subscription
import random
import string


def get_rand_string(length, chars=string.ascii_letters + string.digits):
    return ''.join(random.choice(chars) for _ in range(length))


class Command(BaseCommand):
    args = '<user_amount>'
    help = 'Creates a specified amount of dummy users with templates, subscriptions and dependencies.'

    def handle(self, *args, **options):
        user_count = int(args[0])

        percent_users_with_templates = .95
        mean_templates_per_user = 10
        percent_users_with_subscriptions = .95
        mean_subscriptions_per_user = 5
        percent_public_templates = .2
        mean_dependencies_per_template = 3
        max_dependency_height = 2

        users = {}
        user_names = {}
        templates = {}
        template_names = {}
        templates_for_user = {}
        subscriptions = {}
        ascendant_num = {}
        descendant_num = {}

        print "Creating users"
        it_list = range(user_count)
        length = len(it_list)
        last = 0
        for i in it_list:
            name = get_rand_string(20)
            while name in user_names:
                name = get_rand_string(20)

            u = User(username=name)
            u.set_password(name)

            try:
                u.save()
            except Exception as excp:
                raise CommandError('Could not create user object with name: %s, Exception: %s' % (name, excp))

            user_names[name] = True
            users[u.pk] = u

            percent = (i / float(length))*100
            if percent >= last+5:
                last = (percent // 5) * 5
                print '%d%%' % last

        print "Creating subscriptions"
        # create subscriptions
        it_list = random.sample(users.values(), int(user_count*percent_users_with_subscriptions))
        length = len(it_list)
        last = 0
        i = 0
        for user in it_list:
            for subscribe_to in random.sample(users.values(), int(random.expovariate(1.0/mean_subscriptions_per_user))):
                if user != subscribe_to:
                    try:
                        Subscription.objects.create(subscriber=user, user=subscribe_to)
                    except Exception as excp:
                        raise CommandError('Could not create subscription object from %d to %d, Exception: %s' % (user.pk, subscribe_to.pk, excp))
                    if user.pk in subscriptions:
                        subscriptions[user.pk].append(subscribe_to.pk)
                    else:
                        subscriptions[user.pk] = [subscribe_to.pk, ]

            i += 1
            percent = (i / float(length))*100
            if percent >= last+5:
                last = (percent // 5) * 5
                print '%d%%' % last

        print "Creating templates"
        # create templates
        it_list = random.sample(users.values(), int(user_count*percent_users_with_templates))
        length = len(it_list)
        last = 0
        i = 0
        for user in it_list:
            for j in range(int(round(random.expovariate(1.0/mean_templates_per_user)))):
                name = get_rand_string(20)
                while name in template_names:
                    name = get_rand_string(20)

                is_public = random.uniform(0,1) <= percent_public_templates
                try:
                    template = Template.objects.create(owner=user, name=name, template=name, is_public=is_public)
                except Exception as excp:
                    raise CommandError('Could not create template object with name: %s, Exception: %s' % (name, excp))

                template_names[name] = True
                templates[template.pk] = template
                if user.pk in templates_for_user:
                    templates_for_user[user.pk].append(template)
                else:
                    templates_for_user[user.pk] = [template, ]
                ascendant_num[template.pk] = 0
                descendant_num[template.pk] = 0

            i += 1
            percent = (i / float(length))*100
            if percent >= last+5:
                last = (percent // 5) * 5
                print '%d%%' % last

        print "Creating dependencies"
        # create dependencies
        it_list = templates.values()
        length = len(it_list)
        last = 0
        i = 0
        for template in templates.values():
            candidates = []
            if template.owner_id in templates_for_user:
                candidates += filter(lambda x: (not template.is_public) or x.is_public, templates_for_user[template.owner_id])
            for subscribed_to in subscriptions[template.owner_id] if template.owner_id in subscriptions else []:
                candidates += filter(lambda x: x.is_public, templates_for_user[subscribed_to] if subscribed_to in templates_for_user else [])

            candidates = filter(lambda x: descendant_num[template.pk] + ascendant_num[x.pk] + 1 <= max_dependency_height, candidates)

            for dependency_templ in random.sample(candidates, min(int(random.expovariate(1.0/mean_dependencies_per_template)), len(candidates))):
                try:
                    Template.circular_checker(dependency_templ, template)
                except:
                    continue
                try:
                    template.dependencies.add(dependency_templ)
                except Exception as excp:
                    raise CommandError('Could not create dependency from %s (%d) to %s (%d), Exception: %s' % (template.name, template.pk, dependency_templ.name, dependency_templ.pk, excp))
                ascendant_num[template.pk] = max(ascendant_num[template.pk], ascendant_num[dependency_templ.pk]+1)
                descendant_num[dependency_templ.pk] = max(descendant_num[dependency_templ.pk], descendant_num[template.pk]+1)

            i += 1
            percent = (i / float(length))*100
            if percent >= last+5:
                last = (percent // 5) * 5
                print '%d%%' % last

        print "All done."