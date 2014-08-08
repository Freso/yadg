from descgen.forms import InputForm, SettingsForm, ScratchpadForm, SubscribeForm, UnsubscribeForm, UserSearchForm, TemplateForm, TemplateDeleteForm
from descgen.mixins import CreateTaskMixin, GetTemplateMixin, GetFormatMixin, SerializeResultMixin, CheckResultMixin
from descgen.scraper.factory import SCRAPER_ITEMS
from .visitor.template import TemplateVisitor
from .models import Template, Subscription, Settings
from .result import ReleaseResult

from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import login as contrib_login, logout as contrib_logout
from django.utils.decorators import method_decorator
from django.utils.http import is_safe_url
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from django.http import Http404
from django.views.generic.base import View
from django.views.generic.edit import FormView
from django.views.generic.base import TemplateView, TemplateResponseMixin
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.db.models.query import Q
from django.conf import settings
from django.core.exceptions import ValidationError

from djcelery.models import TaskMeta

import markdown


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


class IndexView(View, CreateTaskMixin):
    
    def get(self, request):
        form = InputForm(self.request.GET)
        if form.is_valid():
            input = form.cleaned_data['input']
            scraper = form.cleaned_data['scraper']
            
            task = self.create_task(input=input, scraper=scraper)
                
            return redirect('get_result',id=task.task_id)
        else:
            form = InputForm(initial={'scraper': self.get_valid_scraper(None)})
        return render(request,'index.html', {'input_form':form})


class ResultView(View):
    
    def get(self, request, id):
        try:
            task = TaskMeta.objects.get(task_id=id)
        except TaskMeta.DoesNotExist:
            return render(request,'result_404.html', status=404)
        if task.status == 'SUCCESS':
            (result, additional_data) = task.result
            visitor = TemplateVisitor(self.request, additional_data, id)

            return visitor.visit(result)

        elif task.status == 'FAILURE' or task.status == 'REVOKED':
            return render(request, 'result_failed.html')
        else:
            return render(request, 'result_waiting.html')


class TemplateListView(ListView):
    template_name = 'template_list.html'
    context_object_name = 'templates'
    paginate_by = 20

    def get_queryset(self):
        return self.request.user.template_set.all()

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(TemplateListView, self).dispatch(request, *args, **kwargs)


class TemplateDeleteView(View, TemplateResponseMixin):
    form_class = TemplateDeleteForm
    template_name = 'template_delete.html'

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
    template_name = 'template_add.html'

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


class TemplateEditView(FormView):
    form_class = TemplateForm
    template_name = 'template_edit.html'
    template = None

    def get_context_data(self, **kwargs):
        ctx = super(TemplateEditView, self).get_context_data(**kwargs)
        ctx['template_id'] = self.kwargs['id']
        if self.template is not None:
            ctx['immediate_dependencies'] = self.template.dependencies.all().select_related('owner')
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
        #return render(self.request, self.template_name, self.get_context_data(form=form, successful=True))

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(TemplateEditView, self).dispatch(request, *args, **kwargs)


class TemplateFromScratchpadView(FormView):
    form_class = ScratchpadForm
    template_name = 'template_from_scratchpad.html'

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
            immediate_dependencies = t.dependencies.all().select_related('owner')
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


class ScratchpadIndexView(View):

    def get(self, request):
        results = TaskMeta.objects.filter(status__exact='SUCCESS').order_by('id')

        task_id = None
        i = 0
        while task_id is None and i < len(results):
            task = results[i]
            temp = task.result[0]
            if isinstance(temp, ReleaseResult):
                task_id = task.task_id
            i += 1

        if task_id is not None:
            redirect_url = reverse('scratchpad', args=(task_id,))
            if self.request.GET:
                redirect_url += '?' + self.request.GET.urlencode()
            return redirect(redirect_url)
        else:
            return render(request, 'scratchpad_index_no_release.html')

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(ScratchpadIndexView, self).dispatch(request, *args, **kwargs)


class ScratchpadView(TemplateView, GetTemplateMixin, GetFormatMixin, SerializeResultMixin, CheckResultMixin):
    template_name = 'scratchpad.html'

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
    

class SettingsView(FormView):
    form_class = SettingsForm
    template_name = 'settings.html'

    def get_form_kwargs(self):
        kwargs = super(SettingsView, self).get_form_kwargs()
        try:
            settings = self.request.user.settings
        except Settings.DoesNotExist:
            settings = Settings(user=self.request.user)
        kwargs['instance'] = settings
        return kwargs
    
    def form_valid(self, form):
        form.save()
        return render(self.request, self.template_name, {'form': form, 'successful': True})

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(SettingsView, self).dispatch(request, *args, **kwargs)


class ScrapersView(TemplateView):
    template_name = 'scrapers_overview.html'

    def get_context_data(self, **kwargs):
        data = super(ScrapersView, self).get_context_data(**kwargs)

        md = markdown.Markdown(output_format='html5', safe_mode='escape')

        scrapers = []

        for scraper in SCRAPER_ITEMS:
            scraper_item = {
                'name': scraper['name'],
                'url': scraper['url'],
                'release': scraper['release'],
                'searchable': scraper['searchable']
            }
            if 'notes' in scraper:
                scraper_item['notes'] = md.convert(scraper['notes'])
            scrapers.append(scraper_item)

        data['scrapers'] = scrapers

        return data


class SubscriptionsView(ListView):
    template_name = 'subscriptions.html'
    context_object_name = 'subscriptions'
    paginate_by = 20

    def get_queryset(self):
        return User.objects.filter(subscriber_set__subscriber__exact=self.request.user).extra(select={'lower_username': 'lower(username)'}).order_by('lower_username')

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(SubscriptionsView, self).dispatch(request, *args, **kwargs)


def login(request, **kwargs):
    if request.user.is_authenticated():
        return redirect(settings.LOGIN_REDIRECT_URL)
    else:
        return contrib_login(request, **kwargs)


@login_required
def logout(request, **kwargs):
    return contrib_logout(request, **kwargs)


def csrf_failure(request, reason=""):
    return render(request, 'csrf_failure.html', status=403)