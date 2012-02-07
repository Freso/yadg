from django import forms
from descgen.scraper.factory import SCRAPER_CHOICES,SCRAPER_DEFAULT
from descgen.formatter import FORMAT_CHOICES,FORMAT_DEFAULT

class InputForm(forms.Form):
    input = forms.CharField(label='Search Term:',widget=forms.TextInput(attrs={'placeholder': 'Enter release url or search term','class':'input-xxlarge'}))
    scraper = forms.ChoiceField(label='Scraper:', choices=SCRAPER_CHOICES, initial=SCRAPER_DEFAULT, widget=forms.Select(attrs={'class':'input-medium'}))

class FormatForm(forms.Form):
    f = forms.ChoiceField(label='Format:', choices=FORMAT_CHOICES, initial=FORMAT_DEFAULT)