#!/usr/bin/python
# -*- coding: utf-8 -*-
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

    @method_decorator(sensitive_post_parameters())
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        return super(RegisterView, self).dispatch(request, *args, **kwargs)