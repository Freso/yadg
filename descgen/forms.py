from django import forms

class InputForm(forms.Form):
    input = forms.CharField(label='Input')