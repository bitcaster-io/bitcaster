# -*- coding: utf-8 -*-
import logging

from constance import config
from django.urls import reverse, reverse_lazy
from django.utils.translation import ugettext as _
from django.views.generic import FormView

from bitcaster.models import Channel
from bitcaster.web.forms.channel import ChannelUpdateConfigurationForm
from bitcaster.web.forms.system_settings import (SettingsEmailForm,
                                                 SettingsMainForm,
                                                 SettingsOAuthForm,)
from bitcaster.web.views import BitcasterTemplateView
from bitcaster.web.views.base import SuperuserViewMixin
from bitcaster.web.views.channel import (ChannelCreateWizard, ChannelDeleteView,
                                         ChannelDeprecateView, ChannelListView,
                                         ChannelToggleView, ChannelUpdateView,)

logger = logging.getLogger(__name__)

__all__ = ["SettingsView", "SettingsOAuthView",
           "SettingsEmailView", "SettingsChannelListView",
           "SettingsChannelUpdateView",
           "SettingsChannelDeleteView",
           "SettingsChannelDeprecateView",
           "SettingsChannelToggleView",
           "SettingsChannelCreateWizard",
           ]


class SettingsBaseView(SuperuserViewMixin,
                       BitcasterTemplateView, FormView):
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


class SettingsChannelCreateWizard(ChannelCreateWizard):
    success_url = reverse_lazy('settings-channels')

    def get_extra_instance_kwargs(self):
        return {'system': True}


class SettingsChannelListView(SuperuserViewMixin, ChannelListView):
    template_name = 'bitcaster/settings/channel_list.html'

    def get_context_data(self, **kwargs):
        kwargs['title'] = _("System channels")
        kwargs['create_url'] = reverse("system-channel-create")
        kwargs['edit_system_channel'] = True
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        return Channel.objects.filter(system=True)


class SettingsChannelUpdateView(SuperuserViewMixin, ChannelUpdateView):
    template_name = 'bitcaster/settings/channel_configure.html'
    form_class = ChannelUpdateConfigurationForm
    success_url = reverse_lazy("settings-channels")

    def get_queryset(self):
        return Channel.objects.filter(system=True)


class SettingsChannelDeleteView(SuperuserViewMixin, ChannelDeleteView):
    template_name = 'bitcaster/settings/channel_remove.html'
    success_url = reverse_lazy("settings-channels")

    def get_queryset(self):
        return Channel.objects.filter(system=True)


class SettingsChannelDeprecateView(SuperuserViewMixin, ChannelDeprecateView):
    pattern_name = "settings-channels"

    def get_queryset(self):
        return Channel.objects.filter(system=True)

    def get_redirect_url(self, *args, **kwargs):
        return reverse_lazy("settings-channels")


class SettingsChannelToggleView(SuperuserViewMixin, ChannelToggleView):
    pattern_name = "settings-channels"

    def get_redirect_url(self, *args, **kwargs):
        return reverse_lazy("settings-channels")

    def get_queryset(self):
        return Channel.objects.filter(system=True)
