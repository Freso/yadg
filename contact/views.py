#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2011-2015 Slack
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from django.views.generic.edit import FormView
from django.views.generic.base import TemplateView
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import redirect

from smtplib import SMTPException

from .forms import ContactForm


class ContactView(FormView):
    form_class = ContactForm
    template_name = 'contact/contact.html'

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
            return redirect('contact_error')
        else:
            return redirect('contact_success')


class ContactSuccessView(TemplateView):
    template_name = 'contact/contact_success.html'


class ContactErrorView(TemplateView):
    template_name = 'contact/contact_error.html'