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

from django.conf import settings
from django.contrib.auth import login as do_login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import login as contrib_login, logout as contrib_logout
from django.shortcuts import redirect
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.cache import never_cache
from django.views.generic import FormView
from django.utils.decorators import method_decorator
from ..forms import UserRegisterForm


@sensitive_post_parameters()
@never_cache
def login(request, **kwargs):
    if request.user.is_authenticated():
        return redirect(settings.LOGIN_REDIRECT_URL)
    else:
        return contrib_login(request, **kwargs)


@login_required
def logout(request, **kwargs):
    return contrib_logout(request, **kwargs)


class RegisterView(FormView):
    form_class = UserRegisterForm
    template_name = 'auth/register.html'

    def form_valid(self, form):
        form.save()
        user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password1'])
        if user is not None:
            do_login(self.request, user)
            return redirect('user_detail', user.pk)
        else:
            # something really weird happened, just redirect to the index
            return redirect('index')

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return redirect(settings.LOGIN_REDIRECT_URL)
        else:
            return super(RegisterView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return redirect(settings.LOGIN_REDIRECT_URL)
        else:
            return super(RegisterView, self).post(request, *args, **kwargs)

    @method_decorator(sensitive_post_parameters())
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        return super(RegisterView, self).dispatch(request, *args, **kwargs)