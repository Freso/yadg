from django import forms
from descgen.scraper.factory import SCRAPER_CHOICES,SCRAPER_DEFAULT
from descgen.formatter import FORMAT_CHOICES,FORMAT_DEFAULT

class InputForm(forms.Form):
    input = forms.CharField(label='Search Term:',widget=forms.TextInput(attrs={'placeholder': 'Enter release url or search term','class':'input-xhlarge'}))
    scraper = forms.ChoiceField(required=False, label='Scraper:', choices=SCRAPER_CHOICES, initial=SCRAPER_DEFAULT, widget=forms.Select(attrs={'class':'auto_width'}))

class FormatForm(forms.Form):
    description_format = forms.ChoiceField(label='Format:', choices=FORMAT_CHOICES, initial=FORMAT_DEFAULT, widget=forms.Select(attrs={'class':'auto_width'}))

class ResultForm(forms.Form):
    description_format = forms.ChoiceField(required=False, label='Format:', choices=FORMAT_CHOICES, initial=FORMAT_DEFAULT)
    include_raw_data = forms.BooleanField(required=False, label='Include raw data:', initial=False)

class SettingsForm(forms.Form):
    description_format = forms.ChoiceField(label='Default Format:', choices=FORMAT_CHOICES, initial=FORMAT_DEFAULT)
    scraper = forms.ChoiceField(label='Default Scraper:', choices=SCRAPER_CHOICES, initial=SCRAPER_DEFAULT)