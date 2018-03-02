# -*- coding: utf-8 -*-
"""
mercury / setup
~~~~~~~~~~~~~~~~~

:copyright: (c) 2018 Stefano Apostolico, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""
from constance import config
from django.utils.translation import ugettext as _
from django import forms
from django.contrib.auth import password_validation
from django.views.generic import TemplateView
from django.views.generic.edit import ProcessFormView, FormMixin

from mercury.models import User


class SetupForm(forms.Form):
    email = forms.EmailField()
    password1 = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput,
        help_text=password_validation.password_validators_help_text_html(),
    )
    password2 = forms.CharField(
        label=_("Password confirmation"),
        widget=forms.PasswordInput,
        strip=False,
        help_text=_("Enter the same password as before, for verification."),
    )

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        return password2


class SetupView(TemplateView, FormMixin, ProcessFormView):
    template_name = 'bitcaster/setup.html'
    form_class = SetupForm
    success_url = '/'

    def form_valid(self, form):
        User.objects.create_superuser(form.cleaned_data['email'],
                                      form.cleaned_data['password1'])
        config.INITIALIZED = 1
        config.save()
        return super().form_valid(form)
