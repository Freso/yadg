#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import login as contrib_login, logout as contrib_logout
from django.shortcuts import redirect
from django.views.decorators.debug import sensitive_post_parameters


@sensitive_post_parameters
def login(request, **kwargs):
    if request.user.is_authenticated():
        return redirect(settings.LOGIN_REDIRECT_URL)
    else:
        return contrib_login(request, **kwargs)


@login_required
def logout(request, **kwargs):
    return contrib_logout(request, **kwargs)