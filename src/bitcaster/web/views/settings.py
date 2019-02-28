# -*- coding: utf-8 -*-
import logging

from constance import config
from django.conf import settings
from django.core.mail import get_connection, send_mail
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView

from bitcaster import messages
from bitcaster.web.forms.system_settings import (SettingsEmailForm,
                                                 SettingsMainForm,
                                                 SettingsOAuthForm,)

from .base import BitcasterTemplateView
from .mixins import SuperuserViewMixin

logger = logging.getLogger(__name__)

__all__ = ['SettingsView', 'SettingsOAuthView',
           'SettingsEmailView',
           # 'SettingsChannelListView',
           # 'SettingsOrgUpdateView',
           # 'SettingsOrgListView',
           'SettingsSystemInfo',
           ]


class SettingsBaseView(SuperuserViewMixin,
                       BitcasterTemplateView, FormView):
    success_url = '.'
    title = ''
    bit = None

    def get_template_names(self):
        return [f'bitcaster/settings/{self.title.lower()}.html',
                'bitcaster/settings/base.html']

    def get_context_data(self, **kwargs):
        kwargs = super(SettingsBaseView, self).get_context_data(**kwargs)
        kwargs['title'] = self.title
        kwargs['settings'] = settings
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
        self.message_user(_('Configuration saved'), messages.SUCCESS)
        if self.bit:
            config.SYSTEM_CONFIGURED |= self.bit
        return super().form_valid(form)


class SettingsView(SettingsBaseView):
    form_class = SettingsMainForm
    title = 'General'
    bit = 1


class SettingsEmailView(SettingsBaseView):
    form_class = SettingsEmailForm
    title = 'Email'
    bit = 2

    def test(self, **kwargs):
        conn = get_connection(
            backend=settings.EMAIL_BACKEND,
            host=kwargs['EMAIL_HOST'],
            username=kwargs['EMAIL_HOST_USER'],
            password=kwargs['EMAIL_HOST_PASSWORD'],
            port=kwargs['EMAIL_HOST_PORT'],
            use_tls=kwargs['EMAIL_USE_TLS'],
            fail_silently=False)
        try:
            return send_mail(subject='test message',
                             message='This is only a test message',
                             connection=conn,
                             from_email=kwargs['EMAIL_SENDER'],
                             recipient_list=[self.request.user.email])
        except Exception:
            return False

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            if request.POST.get('test') == 'Test':
                if self.test(**form.cleaned_data):
                    self.message_user(_('Test succeed. Check your inbox'),
                                      messages.SUCCESS)
                else:
                    self.message_user(_('Configuration problem. Unable to send emails.'),
                                      messages.ERROR)
                return self.form_invalid(form)
            else:
                return self.form_valid(form)
        else:
            return self.form_invalid(form)


class SettingsOAuthView(SettingsBaseView):
    form_class = SettingsOAuthForm
    title = 'Oauth'


# class SettingsOrgUpdateView(SuperuserViewMixin, UpdateView):
#     template_name = 'bitcaster/settings/org_update.html'
#     form_class = OrganizationSystemForm
#     model = Organization
#
#     def get_success_url(self):
#         return reverse('settings-org-list')


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

# class SettingsOrgListView(SuperuserViewMixin, ListView):
#     template_name = 'bitcaster/settings/org_list.html'
#     model = Organization


# class SettingsChannelListView(SuperuserViewMixin, ListView):
#     template_name = 'bitcaster/settings/channel_list.html'
#
#     def get_context_data(self, **kwargs):
#         kwargs['title'] = _('System channels')
#         kwargs['create_url'] = reverse('system-channel-create')
#         return super().get_context_data(**kwargs)
#
#     def get_queryset(self):
#         return Channel.objects.filter(system=True)
