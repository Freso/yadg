from django import forms
from descgen.scraper.factory import SCRAPER_CHOICES,SCRAPER_DEFAULT

class InputForm(forms.Form):
    input = forms.CharField(label='Input')
    scraper = forms.ChoiceField(label='Scraper', choices=SCRAPER_CHOICES, initial=SCRAPER_DEFAULT)