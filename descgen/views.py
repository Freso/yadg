from descgen.forms import InputForm, SettingsForm, SandboxForm, SubscribeForm, UnsubscribeForm, UserSearchForm
from descgen.mixins import CreateTaskMixin, GetFormatMixin
from descgen.scraper.factory import SCRAPER_ITEMS
from .visitor.misc import DescriptionVisitor, JSONSerializeVisitor
from .visitor.template import TemplateVisitor
from .models import Template, Subscription

from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.utils.http import is_safe_url
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from django.http import Http404,HttpResponse
from django.views.generic.base import View
from django.views.generic.edit import FormView
from django.views.generic.base import TemplateView, TemplateResponseMixin
from django.views.generic.list import ListView
from django.db.models.query import Q

from djcelery.models import TaskMeta

import markdown


class UserListView(ListView):
    template_name = 'user_list.html'
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

    def get_context_object_name(self, object_list):
        return 'users'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(UserListView, self).dispatch(request, *args, **kwargs)


class SubscribeView(View):

    def get(self, request):
        return redirect(reverse('user_list'))

    def post(self, request):
        form = SubscribeForm(request.POST)
        if form.is_valid():
            user_id = form.cleaned_data['user_id']
            if user_id != self.request.user.pk and not Subscription.objects.filter(user_id__exact=user_id, subscriber_id__exact=request.user.pk).exists():
                Subscription.objects.create(user_id=user_id, subscriber_id=request.user.pk)
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


class DownloadResultView(View, GetFormatMixin):
    
    def get(self, request, id, format, title):
        try:
            task = TaskMeta.objects.get(task_id=id)
        except TaskMeta.DoesNotExist:
            raise Http404
        format_cleaned = self.get_valid_format(format)
        if task.status != 'SUCCESS' or format_cleaned != format:
            raise Http404
        visitor = DescriptionVisitor(description_format=format_cleaned)
        try:
            result = visitor.visit(task.result[0])
        except visitor.WrongResultType:
            raise Http404
        response = HttpResponse(result,mimetype='text/plain; charset=utf-8')
        return response


class SandboxView(TemplateView):
    template_name = 'sandbox.html'

    def get_context_data(self, id):
        try:
            task = TaskMeta.objects.get(task_id=id)
        except TaskMeta.DoesNotExist:
            raise Http404
        if task.status != 'SUCCESS':
            raise Http404
        visitor = JSONSerializeVisitor()
        result = visitor.visit(task.result[0])
        if result['type'] != 'ReleaseResult':
            raise Http404
        import json
        data = {
            'json_data': json.dumps(result),
            'id': id
        }
        template_list = Template.templates_for_user(self.request.user)
        data['templates'] = sorted(template_list, lambda x,y: cmp(x.name.lower(), y.name.lower()))
        sandbox = SandboxForm()
        if 'template' in self.request.GET:
            t = None
            try:
                pk = int(self.request.GET['template'])
                t = Template.objects.get(pk=pk)
            except Template.DoesNotExist:
                pass
            except ValueError:
                pass
            if t is not None and t in template_list:
                data['template'] = t.template
                data['dependencies'] = {}
                for dep in t.cached_dependencies_set():
                    data['dependencies'][dep.get_unique_name()] = dep.template
                sandbox = SandboxForm(data={'template': t.template})
        data['sandboxform'] = sandbox
        return data
    

class SettingsView(FormView,GetFormatMixin,CreateTaskMixin):
    form_class = SettingsForm
    template_name = 'settings.html'
    
    def get_initial(self):
        initial = {
            'scraper': self.get_valid_scraper(None),
            'description_format': self.get_valid_format(None)
        }
        return initial
    
    def form_valid(self, form):
        self.request.session['default_format'] = form.cleaned_data['description_format']
        self.request.session['default_scraper'] = form.cleaned_data['scraper']
        return render(self.request,self.template_name,{'form':form, 'successful':True})


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


def csrf_failure(request, reason=""):
    return render(request, 'csrf_failure.html', status=403)