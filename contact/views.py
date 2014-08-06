#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.views.generic.edit import FormView
from django.views.generic.base import TemplateView
from django.core.mail import send_mail
from django.conf import settings
from django.core.urlresolvers import reverse
from django.shortcuts import redirect

from smtplib import SMTPException

from .forms import ContactForm


class ContactView(FormView):
    form_class = ContactForm
    template_name = 'contact.html'

    def form_valid(self, form):
        data = form.cleaned_data
        subject = 'YADG contact form'
        if data['subject']:
            subject += ': %s' % data['subject']
        message = data['message']
        if data['from_email']:
            from_email = data['from_email']
        else:
            from_email = settings.SERVER_EMAIL
        recipients = settings.CONTACT_RECIPIENTS
        try:
            send_mail(subject=subject, message=message, from_email=from_email, recipient_list=recipients)
        except SMTPException:
            return redirect(reverse('contact_error'))
        else:
            return redirect(reverse('contact_success'))


class ContactSuccessView(TemplateView):
    template_name = 'contact_success.html'


class ContactErrorView(TemplateView):
    template_name = 'contact_error.html'