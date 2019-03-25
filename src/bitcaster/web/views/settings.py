# -*- coding: utf-8 -*-
import logging

from constance import config
from django.conf import settings
from django.core.mail import get_connection, send_mail
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView

from bitcaster import messages
from bitcaster.web.forms.system_settings import (SettingsEmailForm,
                                                 SettingsLdapForm,
                                                 SettingsMainForm,
                                                 SettingsOAuthForm,)

from .base import BitcasterTemplateView
from .mixins import SidebarMixin, SuperuserViewMixin, TitleMixin

logger = logging.getLogger(__name__)

__all__ = ['SettingsView', 'SettingsOAuthView',
           'SettingsEmailView',
           'SettingsLdapView',
           'SettingsSystemInfo',
           ]


class SettingsTemplateMixin(SuperuserViewMixin, SidebarMixin, TitleMixin,
                            BitcasterTemplateView):

    def get_template_names(self):
        return [f'bitcaster/settings/{self.template_name}.html',
                'bitcaster/settings/form.html']


class SettingsBaseView(SettingsTemplateMixin, FormView):
    success_url = '.'
    bit = None

    def get_form(self, form_class=None):
        form_class = self.get_form_class()
        kwargs = self.get_form_kwargs()
        for f in form_class.declared_fields.keys():
            value = getattr(config, f, '')
            if isinstance(value, dict):
                value = str(value)
            kwargs['initial'][f] = value
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
    title = _('General')
    bit = 1


class SettingsEmailView(SettingsBaseView):
    form_class = SettingsEmailForm
    title = _('Mail Server')
    bit = 2
    template_name = 'email'

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
            prefix = kwargs.get("EMAIL_SUBJECT_PREFIX", None)
            if prefix:
                prefix += " "
            return send_mail(subject=f'{prefix}test message',
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
    title = _('Oauth')
    template_name = 'oauth'


class SettingsLdapView(SettingsBaseView):
    form_class = SettingsLdapForm
    title = _('Ldap')


class SettingsSystemInfo(SettingsTemplateMixin, ):
    template_name = 'environment'
    title = _('Environment')

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
