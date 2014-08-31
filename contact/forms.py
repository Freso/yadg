#!/usr/bin/python
# -*- coding: utf-8 -*-

from django import forms
from captcha.fields import ReCaptchaField


class ContactForm(forms.Form):
    from_email = forms.EmailField(required=False, help_text='Optional. Provide your email address if you would like to receive an answer to your query.')
    subject = forms.CharField(max_length=50, required=False, help_text='Optional. Provide the subject of your message.')
    message = forms.CharField(widget=forms.Textarea(attrs={'class': 'auto_width'}), max_length=4096, help_text="Enter your message here. Please don't use more than 4096 characters.")
    captcha = ReCaptchaField(help_text="Please type in the words to assure you are actually human.")