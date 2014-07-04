from django import forms
from descgen.scraper.factory import SCRAPER_CHOICES,SCRAPER_DEFAULT
from descgen.formatter import FORMAT_CHOICES,FORMAT_DEFAULT
from .models import Template, Subscription
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import ValidationError
from codemirror import CodeMirrorTextarea


search_form_widget_kwargs = {
    'attrs': {
        'class': 'input-medium search-query',
        'placeholder': 'leave empty for all'
    }
}


class InputForm(forms.Form):
    input = forms.CharField(label='Search Term:', max_length=255, widget=forms.TextInput(attrs={'placeholder': 'Enter release url or search term','class':'input-xhlarge'}))
    scraper = forms.ChoiceField(required=False, label='Scraper:', choices=SCRAPER_CHOICES, initial=SCRAPER_DEFAULT, widget=forms.Select(attrs={'class':'auto_width'}))


class FormatForm(forms.Form):
    def __init__(self, user, *args, **kwargs):
        if 'with_utility' in kwargs:
            with_utility = kwargs['with_utility']
            del kwargs['with_utility']
        else:
            with_utility = False
        super(FormatForm, self).__init__(*args, **kwargs)
        self.fields['template'] = forms.ChoiceField(label='Template:',
                                                    choices=map(lambda x: (x.pk, x.name),
                                                                sorted(Template.templates_for_user(user, with_utility=with_utility),
                                                                       lambda x, y: cmp(x.name.lower(), y.name.lower()))),
                                                    widget=forms.Select(attrs={'class': 'auto_width'}))


class ResultForm(forms.Form):
    description_format = forms.ChoiceField(required=False, label='Format:', choices=FORMAT_CHOICES, initial=FORMAT_DEFAULT)
    include_raw_data = forms.BooleanField(required=False, label='Include raw data:', initial=False)


class SettingsForm(forms.Form):
    description_format = forms.ChoiceField(label='Default Format:', choices=FORMAT_CHOICES, initial=FORMAT_DEFAULT)
    scraper = forms.ChoiceField(label='Default Scraper:', choices=SCRAPER_CHOICES, initial=SCRAPER_DEFAULT)


class UserSearchForm(forms.Form):
    username = forms.CharField(label='User: ', required=False, max_length=30, widget=forms.TextInput(**search_form_widget_kwargs))
    template_name = forms.CharField(label='with template: ', required=False, max_length=30, widget=forms.TextInput(**search_form_widget_kwargs))


class SubscribeForm(forms.Form):
    user_id = forms.IntegerField(widget=forms.HiddenInput)

    def clean_user_id(self):
        user_id = self.cleaned_data['user_id']
        try:
            User.objects.get(pk=user_id)
        except User.DoesNotExist:
            raise ValidationError('No valid user id specified')
        return user_id


class UnsubscribeForm(forms.Form):
    next = forms.CharField(widget=forms.HiddenInput, required=False)
    user_id = forms.IntegerField(widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        self.subscriber = kwargs['subscriber']
        kwargs.pop('subscriber')
        super(UnsubscribeForm, self).__init__(*args, **kwargs)

    def clean_user_id(self):
        user_id = self.cleaned_data['user_id']
        try:
            User.objects.get(pk=user_id)
        except User.DoesNotExist:
            raise ValidationError('No valid user id specified')
        if not Subscription.objects.filter(subscriber_id__exact=self.subscriber.pk, user_id__exact=user_id).exists():
            raise ValidationError('You cannot unsubscribe from a user you are not subscribed to.')
        return user_id


class TemplateForm(forms.ModelForm):

    class Meta:
        model = Template
        widgets = {
            'template': CodeMirrorTextarea(mode='swig', config={'lineWrapping': True, 'lineNumbers': True, 'styleActiveLine': True}, theme='neo', keymap='yadg')
        }

    def __init__(self, *args, **kwargs):
        super(TemplateForm, self).__init__(*args, **kwargs)
        if self.instance:
            try:
                u = self.instance.owner
            except ObjectDoesNotExist:
                t = Template.objects.none()
            else:
                t = Template.templates_for_user(u)

            self.fields['dependencies'].queryset = t

    def clean(self):
        dependencies = self.cleaned_data.get('dependencies')

        # make sure there are no circular dependencies
        for dep in dependencies:
            Template.circular_checker(dep, self.instance)

        # make sure a public template only has public dependencies
        is_public = self.cleaned_data.get('is_public')
        if is_public and any([not x.is_public for x in dependencies]):
            raise ValidationError('A template may only be public if all of its dependencies are public.')

        # make sure a default template only has dependencies that are also default
        is_default = self.cleaned_data.get('is_default')
        if is_default and any([not x.is_default for x in dependencies]):
            raise ValidationError('A template may only be a default template if all of its dependencies are default templates.')

        if self.instance.pk and not is_default and any([x.is_default for x in self.instance.depending_set.all()]):
            raise ValidationError('One ore more template depending on this template is a default template. Therefore removing the default status of this template is not allowed.')

        # make sure dependencies are either public templates of users subscribed to or own templates
        u = self.cleaned_data.get('owner')
        if u:
            t = Template.templates_for_user(u)

            if any([(not x in t) for x in dependencies]):
                raise ValidationError('A template may only depend on own templates or public templates of users you are subscribed to.')

        return self.cleaned_data


class SandboxForm(forms.Form):
    template = forms.CharField(widget=CodeMirrorTextarea(keymap='yadg', mode='swig', config={'lineWrapping': True, 'lineNumbers': True, 'styleActiveLine': True}, theme='neo', js_var_format='%s_editor'), initial='Please enter you description template')