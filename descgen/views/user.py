#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from django.utils.http import is_safe_url
from django.views.generic import ListView, DetailView, View
from django.views.generic.base import TemplateResponseMixin
from descgen.forms import UserSearchForm, SubscribeForm, UnsubscribeForm
from descgen.models import Template, Subscription


class UserListView(ListView):
    template_name = 'user_list.html'
    context_object_name = 'users'
    paginate_by = 10
    form = None

    def get_queryset(self):
        self.form = UserSearchForm(self.request.GET)
        if self.form.is_valid():
            user_name = self.form.cleaned_data['username']
            template_name = self.form.cleaned_data['template_name']
            query = Q()
            if user_name:
                query &= Q(username__icontains=user_name)
            if template_name:
                query &= Q(template__name__icontains=template_name) & (Q(template__is_public__exact=True) | Q(template__is_default__exact=True) | Q(template__owner_id__exact=self.request.user.pk))
            queryset = User.objects.filter(query).distinct().extra(select={'lower_username': 'lower(username)'}).order_by('lower_username').prefetch_related('template_set')
        else:
            queryset = User.objects.none()
        return queryset

    def get_context_data(self, **kwargs):
        ret = super(UserListView, self).get_context_data(**kwargs)
        ret['user_search_form'] = self.form
        return ret

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(UserListView, self).dispatch(request, *args, **kwargs)


class UserDetailView(DetailView):
    template_name = 'user_detail.html'
    model = User
    pk_url_kwarg = 'id'
    context_object_name = 'user_obj'

    def get_context_data(self, **kwargs):
        ctx = super(UserDetailView, self).get_context_data(**kwargs)
        user = ctx[self.context_object_name]
        ctx['num_subscribers'] = user.subscriber_set.count()
        ctx['num_templates'] = user.template_set.count()
        ctx['num_public_templates'] = Template.public_templates.filter(owner__exact=user).count()
        ctx['public_percent'] = round(ctx['num_public_templates'] / float(ctx['num_templates']) * 100, 2)
        return ctx

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(UserDetailView, self).dispatch(request, *args, **kwargs)


class SubscribeView(View):

    def get(self, request):
        return redirect(reverse('user_list'))

    def post(self, request):
        form = SubscribeForm(request.POST)
        if form.is_valid():
            user_id = form.cleaned_data['user_id']
            subscription = Subscription(user_id=user_id, subscriber_id=request.user.pk)
            try:
                subscription.full_clean()
            except ValidationError:
                pass
            else:
                subscription.save()
            redirect_to = request.GET.get('next', '')
            if is_safe_url(redirect_to):
                return redirect(redirect_to)
            else:
                return redirect(reverse('user_list'))
        else:
            return render(request, 'user_does_not_exist.html')

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(SubscribeView, self).dispatch(request, *args, **kwargs)


class UnsubscribeView(View, TemplateResponseMixin):
    template_name = 'unsubscribe.html'

    def get(self, request):
        initial = self.get_initial()
        context = {
            'form': UnsubscribeForm(subscriber=self.request.user, initial=initial)
        }
        try:
            id = int(initial['user_id'])
            u = User.objects.get(pk=id)
        except:
            pass
        else:
            context['unsub_user'] = u
            deps = Template.dependencies.through.objects.filter(from_template__owner_id__exact=self.request.user.pk, to_template__owner_id__exact=u.pk, to_template__is_default__exact=False).select_related('from_template')
            context['dependant_templates'] = set(map(lambda x: x.from_template, deps))
        return self.render_to_response(context)

    def post(self, request):
        form = UnsubscribeForm(self.request.POST, subscriber=request.user)
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.render_to_response({'form': form})

    def get_initial(self):
        initial = {
            'user_id': self.request.GET.get('user_id', None),
            'next': self.request.GET.get('next', None)
        }
        return initial

    def form_valid(self, form):
        user_id = form.cleaned_data['user_id']
        subscriber_id = self.request.user.pk
        Subscription.objects.filter(subscriber_id__exact=subscriber_id, user_id__exact=user_id).delete()
        next = form.cleaned_data['next']
        if is_safe_url(next):
            return redirect(next)
        return redirect(reverse('user_list'))

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(UnsubscribeView, self).dispatch(request, *args, **kwargs)


class SubscriptionsView(ListView):
    template_name = 'subscriptions.html'
    context_object_name = 'subscriptions'
    paginate_by = 20

    def get_queryset(self):
        return User.objects.filter(subscriber_set__subscriber__exact=self.request.user).extra(select={'lower_username': 'lower(username)'}).order_by('lower_username')

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(SubscriptionsView, self).dispatch(request, *args, **kwargs)