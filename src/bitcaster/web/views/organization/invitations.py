import logging

from constance import config
from django.contrib.auth import login, logout
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.hashers import make_password
from django.db import transaction
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.functional import cached_property
from django.utils.translation import ugettext as _
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import CreateView
from strategy_field.utils import fqn

from bitcaster import messages
from bitcaster.framework.db.fields import ROLES
from bitcaster.models import Invitation, Organization, OrganizationMember, User
from bitcaster.otp import totp
from bitcaster.web.forms import (OrganizationInvitationFormSet,
                                 UserInviteRegistrationForm,)
from bitcaster.web.views.invitations import (InvitationCreate,
                                             InvitationDelete, InvitationSend,)
from bitcaster.web.views.mixins import MessageUserMixin

from .org import OrganizationBaseView

logger = logging.getLogger(__name__)


class OrgInviteMixin(OrganizationBaseView):
    model = Invitation

    def get_success_url(self):
        return self.selected_organization.urls.members

    def get_queryset(self):
        return self.selected_organization.invitations


class OrganizationMemberInvite(OrgInviteMixin, InvitationCreate):
    form_class = OrganizationInvitationFormSet
    template_name = 'bitcaster/organization/members/invite.html'
    title = _('Invite people')

    def get_parent_instance(self):
        return self.selected_organization


# class OrganizationInvite(OrgInviteMixin, BitcasterBaseCreateView):
#     form_class = OrganizationInvitationFormSet
#     template_name = 'bitcaster/organization/members/invite.html'
#
#     def get_context_data(self, **kwargs):
#         data = super(OrganizationInvite, self).get_context_data(**kwargs)
#         data['invitations'] = data['form']
#         return data
#
#     def get_form(self, form_class=None):
#         form = super().get_form(form_class)
#         form.instance = self.selected_organization
#         return form

# def get_form_class(self):
#     return OrganizationInvitationFormSet

# def form_invalid(self, form):
#     self.message_user(_('invalid'), messages.WARNING)
#     return super(OrganizationInvite, self).form_invalid(form)
#
# def form_valid(self, form):
#     sent = False
#     form.instance = self.selected_organization
# for inline_form in form.extra_forms:
#     if not inline_form.has_changed():
#         continue
#     recipient = inline_form.cleaned_data.get('email', None)
#     if recipient:
#         if not self.selected_organization.memberships.filter(email=recipient).exists():
#             inline_form.instance.organization = self.selected_organization
#             inline_form.instance.invited_by = self.request.user
#             membership = inline_form.save()
#             membership.send_email()
#             self.audit_log(AuditEvent.MEMBER_INVITE,
#                            role=membership.get_role_display(),
#                            email=membership.email)
#             sent = True
#         else:
#             self.message_user(_('Invitation to {0} already sent').format(recipient),
#                               messages.WARNING)
# if sent:
#     self.message_user(_('Invitations sent'), messages.SUCCESS)
# return super(OrganizationInvite, self).form_valid(form)


class OrganizationMemberInviteAccept(MessageUserMixin, CreateView):
    model = Invitation
    form_class = UserInviteRegistrationForm
    template_name = 'bitcaster/registration/user_welcome.html'

    @cached_property
    def selected_organization(self):  # returns selected office and caches the office
        organization = Organization.objects.get(slug=self.kwargs['org'])
        return organization

    def check_perms(self, *args, **kwargs):
        return True

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            logout(request)
            # return HttpResponseBadRequest("User already logged")
        return super().dispatch(request, *args, **kwargs)

    @method_decorator(sensitive_post_parameters())
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        with transaction.atomic():
            user = User.objects.create(email=form.cleaned_data['email'],
                                       is_active=True,
                                       friendly_name=form.cleaned_data['friendly_name'],
                                       password=make_password(form.cleaned_data['password']),
                                       )
            membership = OrganizationMember.objects.create(organization=self.selected_organization,
                                              user=user,
                                              role=self.invitation.role or ROLES.SUBSCRIBER,
                                              date_enrolled=timezone.now())
            self.invitation.date_accepted = timezone.now()
            self.invitation.save()
            login(self.request, user, backend=fqn(ModelBackend))
            assert self.request.user == user

        # if self.invitation.role in [ROLES.OWNER, ROLES.ADMIN]:
        #     url = reverse('org-dashboard', args=[self.selected_organization.slug])
        # else:
        url = reverse('me', args=[self.selected_organization.slug])
        logger.debug(f'Invitation accepted by user {user.email} with role {membership.role}. '
                     f'Redirecting to {url}')
        return HttpResponseRedirect(url)

    def form_invalid(self, form):
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        if self.invitation:
            kwargs['invitation'] = self.invitation
            kwargs['invitation_id'] = self.invitation.pk  # this is required by oauth
            return super().get_context_data(**kwargs)
        else:
            return {}

    def get_initial(self):
        return {'email': self.invitation.target,
                'friendly_name': self.invitation.target}

    @cached_property
    def invitation(self):
        pk = self.kwargs['pk']
        return Invitation.objects.filter(pk=pk,
                                         organization__slug=self.kwargs['org']).first()

    def get(self, request, **kwargs):
        check = kwargs['check']
        if User.objects.filter(email=self.invitation.target).exists():
            self.message_user(_('Email used'), messages.ERROR)
        if totp.verify(check, valid_window=config.INVITATION_EXPIRE):
            return super(OrganizationMemberInviteAccept, self).get(request, **kwargs)

        self.message_user(_('Invite expired'), messages.ERROR)
        return HttpResponseRedirect('/')


class OrgInviteSend(OrgInviteMixin, InvitationSend):
    pass


class OrgInviteDelete(OrgInviteMixin, InvitationDelete):
    pass
