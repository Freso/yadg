#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import Http404
from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from django.views.generic import FormView, View, TemplateView
from djcelery.models import TaskMeta
from descgen.forms import ScratchpadForm, TemplateForm
from descgen.mixins import GetTemplateMixin, GetFormatMixin, SerializeResultMixin, CheckResultMixin
from descgen.models import Template


class TemplateFromScratchpadView(FormView, GetTemplateMixin):
    form_class = ScratchpadForm
    template_name = 'scratchpad/template_from_scratchpad.html'

    def get(self, request, *args, **kwargs):
        return redirect(reverse('scratchpad_index'))

    def form_valid(self, form):
        template_code = form.cleaned_data['template_code']
        t = Template(owner=self.request.user)
        immediate_dependencies = None
        id = None
        if 'id' in self.kwargs and self.kwargs['id']:
            id = int(self.kwargs['id'])
            try:
                t = Template.objects.get(pk=id, owner_id__exact=self.request.user.pk)
            except Template.DoesNotExist:
                raise Http404
            immediate_dependencies = self.get_immediate_dependencies(t, prefetch_owner=True)
        t.template = template_code
        new_form = TemplateForm(instance=t)
        ctx = {
            'form': new_form
        }
        if immediate_dependencies is not None:
            ctx['immediate_dependencies'] = immediate_dependencies
        if id is not None:
            ctx['template_id'] = id
        return self.render_to_response(ctx)

    def form_invalid(self, form):
        return redirect(reverse('scratchpad_index'))

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(TemplateFromScratchpadView, self).dispatch(request, *args, **kwargs)


class ScratchpadIndexView(View, CheckResultMixin):

    def get(self, request):
        results = TaskMeta.objects.filter(status__exact='SUCCESS').order_by('id')

        task_id = None
        i = 0
        while task_id is None and i < len(results):
            task = results[i]
            temp = task.result[0]
            if self.is_release_result(temp):
                task_id = task.task_id
            i += 1

        if task_id is not None:
            redirect_url = reverse('scratchpad', args=(task_id,))
            if self.request.GET:
                redirect_url += '?' + self.request.GET.urlencode()
            return redirect(redirect_url)
        else:
            return render(request, 'scratchpad/scratchpad_index_no_release.html')

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(ScratchpadIndexView, self).dispatch(request, *args, **kwargs)


class ScratchpadView(TemplateView, GetTemplateMixin, GetFormatMixin, SerializeResultMixin, CheckResultMixin):
    template_name = 'scratchpad/scratchpad.html'

    def get_context_data(self, id):
        try:
            task = TaskMeta.objects.get(task_id=id)
        except TaskMeta.DoesNotExist:
            raise Http404
        if task.status != 'SUCCESS':
            raise Http404

        task_result = task.result[0]

        if not self.is_release_result(task_result):
            raise Http404

        data = {
            'json_data': self.serialize_to_json(task_result),
            'id': id,
            'release_title': self.get_release_title(task_result)
        }

        scratchpad = ScratchpadForm()

        template, form = self.get_template_and_form(with_utility=True)

        data['visible_templates_ids'] = map(lambda x: x[0], form.fields['template'].choices)
        if template is not None:
            data['template'] = template
            data['dependencies'] = self.get_all_dependencies(template, prefetch_owner=True)
            data['immediate_dependencies'] = self.get_immediate_dependencies(template, prefetch_owner=True)

            scratchpad = ScratchpadForm(data={'template_code': template.template})

        data['scratchpadform'] = scratchpad

        data['format_form'] = form

        return data

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(ScratchpadView, self).dispatch(request, *args, **kwargs)