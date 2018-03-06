# -*- coding: utf-8 -*-
"""
mercury / settings
~~~~~~~~~~~~~~~~~

:copyright: (c) 2018 Stefano Apostolico, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

import logging

from constance import config
from django.views.generic import FormView
from django.utils.translation import ugettext as _
from mercury.web.forms import (SettingsEmailForm, SettingsMainForm,
                               SettingsOAuthForm, )
from mercury.web.views import MercuryTemplateView
from mercury.web.views.base import SuperuserViewMixin

logger = logging.getLogger(__name__)

__all__ = ["SettingsView", "SettingsOAuthView",
           "SettingsEmailView", "SettingsChannelView"]


class SettingsBaseView(SuperuserViewMixin,
                       MercuryTemplateView, FormView):
    success_url = '.'
    title = ""

    def get_template_names(self):
        return [f'bitcaster/settings/{self.title.lower()}.html',
                'bitcaster/settings/base.html']

    def get_context_data(self, **kwargs):
        kwargs = super(SettingsBaseView, self).get_context_data(**kwargs)
        kwargs['title'] = self.title
        return kwargs

    def get_form(self, form_class=None):
        form_class = self.get_form_class()
        kwargs = self.get_form_kwargs()
        kwargs['initial'] = dict({(f, getattr(config, f, ''))
                                  for f in form_class.declared_fields.keys()})
        return form_class(**kwargs)

    def form_valid(self, form):
        for k, v in form.cleaned_data.items():
            setattr(config, k, v)
        self.message_user(_("Configuration saved"))
        return super().form_valid(form)


class SettingsView(SettingsBaseView):
    form_class = SettingsMainForm
    title = 'General'


class SettingsEmailView(SettingsBaseView):
    form_class = SettingsEmailForm
    title = 'Email'


class SettingsOAuthView(SettingsBaseView):
    form_class = SettingsOAuthForm
    title = 'Oauth'


class SettingsChannelView(MercuryTemplateView):
    template_name = 'bitcaster/settings/channels.html'
    title = 'Channels'
