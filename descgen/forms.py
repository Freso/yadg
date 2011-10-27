from django import forms
from descgen.scraper.factory import SCRAPER_CHOICES,SCRAPER_DEFAULT
from descgen.formatter import FORMAT_CHOICES,FORMAT_DEFAULT

class InputForm(forms.Form):
    input = forms.CharField(label='Input')
    scraper = forms.ChoiceField(label='Scraper', choices=SCRAPER_CHOICES, initial=SCRAPER_DEFAULT)

class FormatForm(forms.Form):
    f = forms.ChoiceField(label='Format', choices=FORMAT_CHOICES, initial=FORMAT_DEFAULT)