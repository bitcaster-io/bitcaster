# -*- coding: utf-8 -*-
import logging

from constance import config
from django.conf import settings
from django.urls import reverse, reverse_lazy
from django.utils.translation import ugettext as _
from django.views.generic import FormView

from bitcaster.models import Channel
from bitcaster.web.forms.channel import ChannelUpdateConfigurationForm
from bitcaster.web.forms.organization import OrganizationSystemForm
from bitcaster.web.forms.system_settings import (SettingsEmailForm,
                                                 SettingsMainForm,
                                                 SettingsOAuthForm,)
from bitcaster.web.views import (BitcasterTemplateView, ListView,
                                 Organization, UpdateView,)
from bitcaster.web.views.base import SuperuserViewMixin
from bitcaster.web.views.channel import (ChannelCreateWizard, ChannelDeleteView,
                                         ChannelDeprecateView,
                                         ChannelToggleView, ChannelUpdateView,)

logger = logging.getLogger(__name__)

__all__ = ["SettingsView", "SettingsOAuthView",
           "SettingsEmailView", "SettingsChannelListView",
           "SettingsChannelUpdateView",
           "SettingsChannelDeleteView",
           "SettingsChannelDeprecateView",
           "SettingsChannelToggleView",
           "SettingsOrgUpdateView",
           "SettingsOrgListView",
           "SettingsSystemInfo",
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


class SettingsOrgUpdateView(SuperuserViewMixin, UpdateView):
    template_name = 'bitcaster/settings/org_update.html'
    form_class = OrganizationSystemForm
    model = Organization

    def get_success_url(self):
        return reverse('settings-org-list')


class SettingsSystemInfo(SuperuserViewMixin,
                         BitcasterTemplateView):
    template_name = 'bitcaster/settings/sysinfo.html'

    def _filter(self, target):
        reserved = ('PASSWORD', 'SECRET', 'KEY', 'AUTHENTICATION_BACKENDS')
        hidden = ('CONSTANCE', 'SOCIAL_AUTH')
        ret = []
        for k in sorted(dir(target)):
            v_repr = repr(getattr(target, k))
            if any(r.lower() in v_repr.lower() for r in hidden):
                continue
            if any(r in k for r in hidden):
                continue
            if k.startswith('_'):
                continue
            if k.upper() != k:
                continue

            if any(r.lower() in v_repr.lower() for r in reserved):
                v_repr = '*' * 16
            if any(r in k for r in reserved):
                v_repr = '*' * 16

            ret.append((k, v_repr))
        return ret

    def get_context_data(self, **kwargs):
        from django_sysinfo.api import get_sysinfo

        return super().get_context_data(
            config=self._filter(config),
            settings=self._filter(settings),
            sysinfo=get_sysinfo(self.request),
            **kwargs)


class SettingsOrgListView(SuperuserViewMixin, ListView):
    template_name = 'bitcaster/settings/org_list.html'
    model = Organization


class SettingsOAuthView(SettingsBaseView):
    form_class = SettingsOAuthForm
    title = 'Oauth'


class SettingsChannelCreateWizard(ChannelCreateWizard):
    success_url = reverse_lazy('settings-channels')

    def get_extra_instance_kwargs(self):
        return {'system': True}


class SettingsChannelListView(SuperuserViewMixin, ListView):
    template_name = 'bitcaster/settings/channel_list.html'

    def get_context_data(self, **kwargs):
        kwargs['title'] = _("System channels")
        kwargs['create_url'] = reverse("system-channel-create")
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
