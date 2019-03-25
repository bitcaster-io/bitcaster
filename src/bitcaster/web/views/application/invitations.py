import logging

from django.utils.translation import ugettext as _

from bitcaster.models.invitation import Invitation
from bitcaster.web.forms.invitations import ApplicationInvitationFormSet
from bitcaster.web.views.invitations import (InvitationCreate,
                                             InvitationDelete, InvitationSend,)

from .app import ApplicationViewMixin

logger = logging.getLogger(__name__)


class ApplicationInvitationMixin(ApplicationViewMixin):
    model = Invitation

    def get_success_url(self):
        return self.selected_application.urls.subscriptions

    def get_queryset(self):
        return self.selected_application.invitations


class ApplicationInvite(ApplicationInvitationMixin, InvitationCreate):
    form_class = ApplicationInvitationFormSet
    template_name = 'bitcaster/application/subscriptions/invite.html'
    title = _('Invite people')

    def get_parent_instance(self):
        return self.selected_application


class ApplicationInvitationDelete(ApplicationInvitationMixin, InvitationDelete):
    pass


class ApplicationInvitationSend(ApplicationInvitationMixin, InvitationSend):
    pass
