import datetime
import glob
import json
import logging
import os

from constance import config
from django.conf import settings
from django.core.mail import get_connection, send_mail
from django.http import HttpResponse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView, RedirectView
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import JsonLexer

from bitcaster import messages
from bitcaster.models import AgentMetaData, Channel, DispatcherMetaData, Monitor
from bitcaster.utils.backup import backup_data
from bitcaster.utils.reflect import fqn
from bitcaster.web.forms.system_settings import (SettingsEmailForm,
                                                 SettingsLdapForm,
                                                 SettingsMainForm,
                                                 SettingsOAuthForm,
                                                 SettingsServicesForm,)

from .base import BitcasterTemplateView, HttpResponseRedirectToReferrer
from .mixins import (MessageUserMixin, SidebarMixin,
                     SuperuserViewMixin, TitleMixin,)

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


class SettingsServicesView(SettingsBaseView):
    form_class = SettingsServicesForm
    title = _('External services')
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
            prefix = kwargs.get('EMAIL_SUBJECT_PREFIX', None)
            if prefix:
                prefix += ' '
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


class SettingsPluginToggle(MessageUserMixin, RedirectView):
    def get_queryset(self):
        if self.kwargs['type'] == 'd':
            return DispatcherMetaData.objects.all()
        else:
            return AgentMetaData.objects.all()

    def get(self, request, *args, **kwargs):
        obj = self.get_queryset().get(pk=self.kwargs['pk'])
        obj.enabled = not obj.enabled
        obj.save()
        if obj.enabled:
            self.message_user(f'{obj.fqn} enabled',
                              level=messages.SUCCESS)
        else:
            if self.kwargs['type'] == 'd':
                if Channel.objects.filter(handler=fqn(obj.handler)).exists():
                    self.alarm(_('You have disabled a dispatecher used by one or more Channels'))
            else:
                if Monitor.objects.filter(handler=fqn(obj.handler)).exists():
                    self.alarm(_('You have disabled a agent used by one or more Monitor'))
            self.message_user(f'{obj.fqn} disabled',
                              level=messages.WARNING)
        return HttpResponseRedirectToReferrer(request)


class SettingsPluginRefresh(SettingsTemplateMixin, ):

    def get(self, request, *args, **kwargs):
        DispatcherMetaData.objects.inspect()
        AgentMetaData.objects.inspect()
        return HttpResponseRedirectToReferrer(request)


class SettingsPlugin(SettingsTemplateMixin, ):
    template_name = 'plugins'
    title = _('Plugins')

    def get_context_data(self, **kwargs):
        if self.kwargs['type'] == 'd':
            plugin_list = DispatcherMetaData.objects.all()
        else:
            plugin_list = AgentMetaData.objects.all()
        return super().get_context_data(plugin_list=plugin_list, **kwargs)


class SettingsBackupRestore(SettingsTemplateMixin):
    template_name = 'backup'
    title = _('Backup / Restore')

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        if 'file' in request.GET:
            filename = request.GET['file']
            dest = os.path.join(config.BACKUPS_LOCATION, filename)

            if 'view' in request.GET:
                context['title'] = _('Backup / Restore: %s') % filename
                json_object = json.load(open(dest))
                json_str = json.dumps(json_object, indent=2, sort_keys=True)
                formatter = HtmlFormatter(linenos='table')
                context['css'] = formatter.get_style_defs()
                context['json'] = mark_safe(highlight(json_str, JsonLexer(), formatter))
            elif 'delete' in request.GET:
                os.unlink(dest)
                return HttpResponseRedirectToReferrer(request)
            elif 'dn' in request.GET:
                with open(dest, 'r'):
                    from django.utils.encoding import smart_str
                    from wsgiref.util import FileWrapper
                    wrapper = FileWrapper(open(dest))

                    response = HttpResponse(wrapper, content_type='application/force-download')
                    response['Content-Disposition'] = 'attachment; filename=%s' % smart_str(filename)
                    response['Content-Length'] = os.path.getsize(dest)
                    return response

        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        today = datetime.date.today()

        dest = os.path.join(config.BACKUPS_LOCATION, today.strftime('%Y-%m-%d.json'))

        backup_data(dest, lambda x: True)
        return HttpResponseRedirectToReferrer(request)

    def get_context_data(self, **kwargs):
        # file_list = [f for f in os.listdir(config.BACKUPS_LOCATION) if os.path.isfile(f)]
        file_list = sorted([os.path.basename(f)
                            for f in glob.glob('%s/*.json' % config.BACKUPS_LOCATION)],
                           reverse=True)
        # return {'file_list':file_list}
        return super().get_context_data(file_list=file_list, **kwargs)
