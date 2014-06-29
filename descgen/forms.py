from django import forms
from descgen.scraper.factory import SCRAPER_CHOICES,SCRAPER_DEFAULT
from descgen.formatter import FORMAT_CHOICES,FORMAT_DEFAULT
from .models import Template
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.query import Q


class InputForm(forms.Form):
    input = forms.CharField(label='Search Term:', max_length=255, widget=forms.TextInput(attrs={'placeholder': 'Enter release url or search term','class':'input-xhlarge'}))
    scraper = forms.ChoiceField(required=False, label='Scraper:', choices=SCRAPER_CHOICES, initial=SCRAPER_DEFAULT, widget=forms.Select(attrs={'class':'auto_width'}))


class FormatForm(forms.Form):
    description_format = forms.ChoiceField(label='Format:', choices=FORMAT_CHOICES, initial=FORMAT_DEFAULT, widget=forms.Select(attrs={'class':'auto_width'}))


class ResultForm(forms.Form):
    description_format = forms.ChoiceField(required=False, label='Format:', choices=FORMAT_CHOICES, initial=FORMAT_DEFAULT)
    include_raw_data = forms.BooleanField(required=False, label='Include raw data:', initial=False)


class SettingsForm(forms.Form):
    description_format = forms.ChoiceField(label='Default Format:', choices=FORMAT_CHOICES, initial=FORMAT_DEFAULT)
    scraper = forms.ChoiceField(label='Default Scraper:', choices=SCRAPER_CHOICES, initial=SCRAPER_DEFAULT)


class TemplateForm(forms.ModelForm):

    class Meta:
        model = Template

    def __init__(self, *args, **kwargs):
        super(TemplateForm, self).__init__(*args, **kwargs)
        if self.instance:
            try:
                u = self.instance.owner
            except ObjectDoesNotExist:
                t = Template.objects.all()
            else:
                us = u.subscribed_to.values('user_id').distinct()
                t = Template.objects.filter(Q(owner__in=us, is_public__exact=True) | Q(owner__exact=u.pk))

            self.fields['dependencies'].queryset = t

    def clean(self):
        from django.core.exceptions import ValidationError

        dependencies = self.cleaned_data.get('dependencies')

        # make sure there are no circular dependencies
        for dep in dependencies:
            Template.circular_checker(dep, self.instance)

        # make sure a public template only has public dependencies
        is_public = self.cleaned_data.get('is_public')
        if is_public and any([not x.is_public for x in dependencies]):
            raise ValidationError('A template may only be public if all of its dependencies are public.')

        # make sure dependencies are either public templates of users subscribed to or own templates
        u = self.cleaned_data.get('owner')
        if u:
            us = u.subscribed_to.values('user_id').distinct()
            t = Template.objects.filter(Q(owner__in=us, is_public__exact=True) | Q(owner__exact=u.pk))

            if any([(not x in t) for x in dependencies]):
                raise ValidationError('A template may only depend on own templates or public templates of users you are subscribed to.')

        return self.cleaned_data