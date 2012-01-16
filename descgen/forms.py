from django import forms
from descgen.scraper.factory import SCRAPER_CHOICES,SCRAPER_DEFAULT,ScraperFactory
from descgen.formatter import FORMAT_CHOICES,FORMAT_DEFAULT

class InputForm(forms.Form):
    input = forms.CharField(label='Search Term:',widget=forms.TextInput(attrs={'placeholder': 'Enter release url or search term','class':'input-xhlarge'}))
    scraper = forms.ChoiceField(label='Scraper:', choices=SCRAPER_CHOICES, initial=SCRAPER_DEFAULT, widget=forms.Select(attrs={'class':'auto_width'}))

class FormatForm(forms.Form):
    f = forms.ChoiceField(label='Format:', choices=FORMAT_CHOICES, initial=FORMAT_DEFAULT, widget=forms.Select(attrs={'class':'auto_width'}))
    
class IdQueryForm(forms.Form):
    id = forms.CharField(label='ID')
    scraper = forms.ChoiceField(label='Scraper', choices=SCRAPER_CHOICES, initial=SCRAPER_DEFAULT)
    
    def clean(self):
        cleaned_data = self.cleaned_data
        id = cleaned_data.get('id')
        scraper = cleaned_data.get('scraper')
        
        if id and scraper:
            factory = ScraperFactory()
            try:
                # try to get a release with the given id
                release = factory.get_release_by_id(id,scraper)
            except ValueError:
                # the id is malformed, add a field error
                msg = "The ID is malformed."
                self._errors["id"] = self.error_class([msg])
                
                # This field is no longer valid. Remove it from the cleaned data.
                del cleaned_data["id"]
        
        # Always return the full collection of cleaned data.
        return cleaned_data
