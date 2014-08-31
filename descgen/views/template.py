#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import Http404
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.generic import ListView, View, FormView
from django.views.generic.base import TemplateResponseMixin
from descgen.forms import TemplateDeleteForm, TemplateForm
from descgen.models import Template
from ..mixins import GetTemplateMixin


class TemplateListView(ListView):
    template_name = 'template/template_list.html'
    context_object_name = 'templates'
    paginate_by = 20

    def get_queryset(self):
        return self.request.user.template_set.all()

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(TemplateListView, self).dispatch(request, *args, **kwargs)


class TemplateDeleteView(View, TemplateResponseMixin):
    form_class = TemplateDeleteForm
    template_name = 'template/template_delete.html'

    def get(self, request):
        form = self.form_class(request.GET, user=self.request.user)
        if form.is_valid():
            t = Template.objects.filter(id__in=form.cleaned_data['to_delete'])
            d_values = Template.dependencies.through.objects.filter(Q(to_template__in=t) & ~Q(from_template__in=t) & Q(from_template__owner_id__exact=self.request.user.pk)).values('from_template_id').distinct()
            d = Template.objects.filter(id__in=d_values)
            other_users_template_count = Template.dependencies.through.objects.filter(Q(to_template__in=t) & ~Q(from_template__owner_id__exact=self.request.user.pk)).values('from_template_id').distinct().count()
            return self.render_to_response({'to_delete': t, 'dependencies': d, 'other_users_template_count': other_users_template_count})
        else:
            return redirect(reverse('template_list'))

    def post(self, request):
        form = self.form_class(request.POST, user=self.request.user)
        if form.is_valid():
            Template.objects.filter(id__in=form.cleaned_data['to_delete']).delete()
            return redirect(reverse('template_list'))
        else:
            return self.render_to_response({'form': form})

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(TemplateDeleteView, self).dispatch(request, *args, **kwargs)


class TemplateAddView(FormView):
    form_class = TemplateForm
    template_name = 'template/template_add.html'

    def get_form_kwargs(self):
        kwargs = super(TemplateAddView, self).get_form_kwargs()
        kwargs['instance'] = Template(owner_id=self.request.user.pk)
        return kwargs

    def form_valid(self, form):
        form.save()
        return redirect(reverse('template_list'))

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(TemplateAddView, self).dispatch(request, *args, **kwargs)


class TemplateEditView(FormView, GetTemplateMixin):
    form_class = TemplateForm
    template_name = 'template/template_edit.html'
    template = None

    def get_context_data(self, **kwargs):
        ctx = super(TemplateEditView, self).get_context_data(**kwargs)
        ctx['template_id'] = self.kwargs['id']
        if self.template is not None:
            ctx['immediate_dependencies'] = self.get_immediate_dependencies(self.template, prefetch_owner=True)
        return ctx

    def get_form_kwargs(self):
        kwargs = super(TemplateEditView, self).get_form_kwargs()
        template_id = int(self.kwargs['id'])
        template = Template.objects.filter(owner_id__exact=self.request.user.pk, pk=template_id)
        if template:
            kwargs['instance'] = self.template = template[0]
        else:
            raise Http404
        return kwargs

    def form_valid(self, form):
        form.save()
        return redirect(reverse('template_list'))

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(TemplateEditView, self).dispatch(request, *args, **kwargs)