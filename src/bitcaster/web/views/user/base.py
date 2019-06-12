import logging

import requests
from constance import config
from django.core.cache import cache
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView
from pytz import country_timezones

from bitcaster.models import User
from bitcaster.models.audit import AuditEvent
from bitcaster.utils.email_verification import set_request_new_email_address
from bitcaster.utils.wsgi import get_client_ip
from bitcaster.web import messages
from bitcaster.web.forms import UserProfileForm, send_address_verification_email
from bitcaster.web.views.organization.mixins import SelectedOrganizationMixin

from ..base import BitcasterBaseUpdateView
from ..mixins import LogAuditMixin, SidebarMixin, TitleMixin

logger = logging.getLogger(__name__)

__all__ = ('UserProfileView',)


class UserMixin(SelectedOrganizationMixin, SidebarMixin, TitleMixin):
    permissions = None


class UserHome(UserMixin, TemplateView):
    template_name = 'bitcaster/user/home.html'
    title = _('Home')

    def get_context_data(self, **kwargs):
        kwargs['missing'] = self.request.user.notifications.missed().distinct('occurence')
        kwargs['invalid'] = self.request.user.addresses.filter(verified=False)
        kwargs['disabled'] = self.request.user.subscriptions.filter(enabled=False)
        return super().get_context_data(**kwargs)


class UserProfileView(UserMixin, LogAuditMixin, BitcasterBaseUpdateView):
    template_name = 'bitcaster/user/profile.html'
    model = User
    form_class = UserProfileForm
    success_url = '.'
    title = _('My Profile')

    def get_object(self, queryset=None):
        return self.request.user

    def get_initial(self):  # noqa C901
        initial = {}
        user = self.get_object()
        if not (user.country and user.timezone and user.language):
            remote_ip = get_client_ip(self.request)
            if remote_ip and config.IPSTACK_KEY:
                try:
                    response = cache.get('ipstack-%s' % remote_ip)
                    if not response:
                        url = '{0}/{2}?access_key={1}'.format(config.IPSTACK_HOST,
                                                              config.IPSTACK_KEY,
                                                              remote_ip)
                        response = requests.get(url).json()

                    if not user.country:
                        try:
                            initial['country'] = response['country_code']
                        except KeyError:  # pragma: no cover
                            initial['country'] = None

                    if not user.language:
                        try:
                            initial['language'] = response['location']['languages'][0]['code']
                        except (KeyError, IndexError):  # pragma: no cover
                            initial['timezone'] = None

                    if not user.timezone:
                        try:
                            initial['timezone'] = country_timezones(initial['country'])
                        except KeyError:  # pragma: no cover
                            initial['timezone'] = None
                    cache.set('ipstack-%s' % remote_ip, response)
                except Exception:  # pragma: no cover
                    pass

        return initial

    def get_context_data(self, **kwargs):
        ret = super().get_context_data(**kwargs)

        if ret['form'].new_email_pending:
            ret['newemail'] = ret['form'].new_email_pending
        return ret

    def form_valid(self, form):
        email_changed = form.fields['email'].has_changed(form.initial.get('email'),
                                                         form.data.get('email'))

        if email_changed:
            set_request_new_email_address(form.instance, form.data['email'])
            send_address_verification_email(form.instance)
            form.instance.email = form.initial['email']
            self.message_user(_('Check your inbox to validate your new email address'), messages.SUCCESS)
        ret = super().form_valid(form)
        self.audit(None, AuditEvent.MEMBER_UPDATE_PROFILE)
        return ret
