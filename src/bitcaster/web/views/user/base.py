import logging

from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView

from bitcaster import messages
from bitcaster.models import User
from bitcaster.models.audit import AuditLogEntry
from bitcaster.utils.email_verification import set_request_new_email_address
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


class UserProfileView(UserMixin, LogAuditMixin, BitcasterBaseUpdateView):
    template_name = 'bitcaster/user/profile.html'
    model = User
    form_class = UserProfileForm
    success_url = '.'
    title = _('My Profile')

    def get_object(self, queryset=None):
        return self.request.user

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
        self.audit(event=AuditLogEntry.AuditEvent.MEMBER_UPDATE_PROFILE)
        return ret
