import logging

from constance import config
from django.contrib.auth import login
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
from django.views.generic.edit import FormMixin, ProcessFormView
from strategy_field.utils import fqn

from bitcaster import messages
from bitcaster.framework.db.fields import ROLES
from bitcaster.models import (AuditLogEntry, Invitation, Organization,
                              OrganizationMember, User,)
from bitcaster.otp import totp
from bitcaster.web.forms import (OrganizationInvitationForm,
                                 UserInviteRegistrationForm,)
from bitcaster.web.views.base import BitcasterTemplateView
from bitcaster.web.views.invitations import InvitationDelete, InvitationSend
from bitcaster.web.views.mixins import LogAuditMixin, MessageUserMixin

from .org import OrganizationBaseView

logger = logging.getLogger(__name__)


class OrgInviteMixin(OrganizationBaseView):
    model = Invitation

    # def get_success_url(self):
    #     return self.selected_organization.urls.members
    #
    # def get_queryset(self):
    #     return self.selected_organization.invitations


class OrganizationMemberInvite(OrganizationBaseView, LogAuditMixin,
                               FormMixin,
                               ProcessFormView,
                               BitcasterTemplateView):
    form_class = OrganizationInvitationForm

    template_name = 'bitcaster/organization/members/invite.html'
    title = _('Invite people')

    def get_success_url(self):
        return self.selected_organization.urls.members

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['organization'] = self.selected_organization
        return kwargs

    def get_context_data(self, **kwargs):
        kwargs['roles'] = ROLES
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        values = {'role': form.cleaned_data['role'],
                  'organization': self.selected_organization,
                  'invited_by': self.request.user}
        for email in form.cleaned_data['emails']:
            values['target'] = email
            invitation = Invitation.objects.create(**values)
            invitation.groups.set(form.cleaned_data['groups'])
            invitation.send_email()
            self.audit(event=AuditLogEntry.AuditEvent.INVITATION_CREATED,
                       actor=invitation.invited_by,
                       target_object=invitation.pk,
                       target_label=str(invitation))

        return super().form_valid(form)

    # def get_parent_instance(self):
    #     return self.selected_organization
    #
    # def form_valid(self, formset):
    #     ret = super().form_valid(formset)
    #     if formset.new_objects:
    #         for invitation in formset.new_objects:
    #             self.audit(event=AuditLogEntry.AuditEvent.INVITATION_CREATED,
    #                        actor=invitation.invited_by,
    #                        target_object=invitation.pk,
    #                        target_label=str(invitation))
    #     return ret


class OrganizationMemberInviteAccept(MessageUserMixin, LogAuditMixin, CreateView):
    model = Invitation
    form_class = UserInviteRegistrationForm
    template_name = 'bitcaster/registration/user_welcome.html'

    @cached_property
    def selected_organization(self):  # returns selected office and caches the office
        organization = Organization.objects.get(slug=self.kwargs['org'])
        return organization

    # def check_perms(self, *args, **kwargs):
    #     return True

    # def dispatch(self, request, *args, **kwargs):
    #     if request.user.is_authenticated:
    #         logout(request)
    #         # return HttpResponseBadRequest("User already logged")
    #     return super().dispatch(request, *args, **kwargs)

    @method_decorator(sensitive_post_parameters())
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        with transaction.atomic():
            user = User.objects.create(email=form.cleaned_data['email'],
                                       is_active=True,
                                       friendly_name=form.cleaned_data['friendly_name'],
                                       password=make_password(form.cleaned_data['password1']),
                                       )
            membership = OrganizationMember.objects.create(organization=self.selected_organization,
                                                           user=user,
                                                           role=self.invitation.role or ROLES.MEMBER,
                                                           date_enrolled=timezone.now())
            for g in self.invitation.groups.all():
                g.members.add(membership)

            self.invitation.date_accepted = timezone.now()
            self.invitation.user = user
            self.invitation.save()
            self.audit(event=AuditLogEntry.AuditEvent.INVITATION_ACCEPTED,
                       actor=user,
                       target_object=self.invitation.pk,
                       target_label=str(self.invitation))

            self.audit(event=AuditLogEntry.AuditEvent.MEMBERSHIP_CREATED,
                       actor=user,
                       target_object=membership.pk,
                       target_label=str(membership))

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
        kwargs['title'] = _('Accept invitation')
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
        if not self.invitation:
            self.message_user(_('Invalid invitation'), messages.ERROR)
            return HttpResponseRedirect('')

        if User.objects.filter(email=self.invitation.target).exists():
            self.message_user(_('Email used'), messages.ERROR)
        if totp.verify(check, valid_window=config.INVITATION_EXPIRE):
            return super().get(request, **kwargs)

        self.message_user(_('Invite expired'), messages.ERROR)
        return HttpResponseRedirect('/login/')


class OrgInviteSend(OrgInviteMixin, InvitationSend):
    pass


class OrgInviteDelete(OrgInviteMixin, InvitationDelete):
    pass
