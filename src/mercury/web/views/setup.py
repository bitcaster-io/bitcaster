# -*- coding: utf-8 -*-
"""
mercury / setup
~~~~~~~~~~~~~~~~~

:copyright: (c) 2018 Stefano Apostolico, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""
from django import forms
from django.views.generic import TemplateView
from django.views.generic.edit import ProcessFormView, FormMixin


class SetupForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)


class SetupView(TemplateView, FormMixin, ProcessFormView):
    template_name = 'bitcaster/setup.html'
    form_class = SetupForm
