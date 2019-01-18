# -*- coding: utf-8 -*-
import logging

from constance import config
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.hashers import make_password
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from django.views.generic import (CreateView, DeleteView, ListView,
                                  RedirectView, UpdateView,)
from strategy_field.utils import fqn

from bitcaster.db.fields import Role
from bitcaster.models import (AuditEvent, Organization, OrganizationMember,
                              Team, TeamMembership, User, audit_log,)
from bitcaster.models.configurationissue import (check_application,
                                                 check_organization,)
from bitcaster.otp import totp
from bitcaster.security import is_owner
from bitcaster.utils.dashboard import check_channels, get_status
from bitcaster.web.forms import (OrganizationForm, OrganizationInvitationForm,
                                 OrganizationInvitationFormSet, TeamForm,
                                 UserInviteRegistrationForm,)
from bitcaster.web.forms.user import NewMemberForm

from .base import (ApplicationListMixin, BitcasterBaseCreateView,
                   BitcasterBaseDeleteView, BitcasterBaseDetailView,
                   BitcasterBaseListView, BitcasterBaseUpdateView,
                   BitcasterFormView, MessageUserMixin,
                   SelectedOrganizationMixin,)
from .channel import (ChannelCreateWizard, ChannelDeleteView,
                      ChannelDeprecateView,
                      ChannelToggleView, ChannelUpdateView,)

logger = logging.getLogger(__name__)

__all__ = ['OrganizationCreate', 'OrganizationDashboard', 'OrganizationUpdate',
           'OrganizationMembershipList', 'OrganizationChannels',
           'OrganizationTeamList', 'OrganizationTeamCreate',
           'OrganizationCheckConfigView',
           'OrganizationChannelRemove', 'OrganizationChannelToggle',
           'OrganizationChannelUpdate', 'OrganizationChannelDeprecate',
           'OrganizationTeamUpdate', 'OrganizationTeamMember',
           'OrganizationMembershipEdit', 'OrganizationMembershipDelete',
           'OrganizationCreateMember',
           'OrganizationInvite', 'InviteDelete', 'InviteSend', 'InviteAccept',
           'OrganizationApplications', 'OrganizationChannelCreate']


class OrganizationAuditMixin:

    def audit_log(self, event, **kwargs):
        audit_log(self.request, event,
                  organization=self.selected_organization,
                  **kwargs)


class OrganizationViewMixin(OrganizationAuditMixin, ApplicationListMixin):
    model = Organization
    slug_url_kwarg = 'org'
    template_name_base = 'organization'

    def dispatch(self, request, *args, **kwargs):
        if not is_owner(request.user, self.selected_organization):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class OrganizationDashboard(OrganizationViewMixin, BitcasterBaseDetailView):
    template_name = 'bitcaster/organization/organization_dashboard.html'

    def get_context_data(self, **kwargs):
        org = self.selected_organization
        cache_key = f'org:dashboard:{org.pk}'
        org_data = cache.get(cache_key, version=org.version)
        if not org_data:
            org_data = {
                'active_users': org.members.count(),
                'pending_users': org.invitations.count(),
                'enabled_channels': org.channels.filter(enabled=True).count(),
                'disabled_channels': org.channels.filter(enabled=False).count(),
                'deprecated_channels': org.channels.filter(deprecated=True).count(),
                'applications': org.applications.count(),
            }
            org_data['box_members'] = get_status(org_data['pending_users'], 0, 1, 9999)
            org_data['box_channels'] = check_channels(org_data)
            org_data['box_apps'] = get_status(org_data['applications'], 1, 9999, 9999)
            cache.set(cache_key, org_data)
        kwargs['data'] = org_data
        kwargs['options'] = dict(org.options.values_list('key', 'value'))
        return super().get_context_data(**kwargs)


class OrganizationCheckConfigView(OrganizationAuditMixin, ApplicationListMixin, RedirectView):
    pattern_name = 'org-dashboard'

    def get(self, request, *args, **kwargs):
        check_organization(self.selected_organization)
        for app in self.selected_organization.applications.all():
            check_application(app)
        return super().get(request, *args, **kwargs)


class OrganizationUpdate(OrganizationViewMixin, BitcasterBaseUpdateView):
    form_class = OrganizationForm
    success_url = '.'

    def form_valid(self, form):
        slug = form.cleaned_data.get('slug', None)
        self.object = form.save()
        url = reverse('org-config', args=[slug or self.object.slug])
        self.message_user(_('Configuration saved'), messages.SUCCESS)
        return HttpResponseRedirect(url)


class OrganizationCreate(OrganizationViewMixin, BitcasterBaseCreateView):
    form_class = OrganizationForm
    success_url = '.'

    def form_valid(self, form):
        form.instance.owner = self.request.user
        self.message_user(_('Organization created'), messages.SUCCESS)
        return super().form_valid(form)


class OrganizationCreateMember(OrganizationViewMixin, CreateView):
    template_name = 'bitcaster/organization_new_member.html'
    model = User
    form_class = NewMemberForm

    def get_success_url(self):
        return reverse('org-member-list',
                       args=[self.selected_organization.slug])

    def form_valid(self, form):
        self.object = form.save()
        self.selected_organization.memberships.create(user=self.object,
                                                      invited_by=self.request.user,

                                                      )
        return super().form_valid(form)

        # return super().form_valid(form)


class OrganizationMembershipList(OrganizationViewMixin, BitcasterBaseListView):
    # form_class = OrganizationForm
    # template_name = 'bitcaster/organization/member_list.html'
    success_url = '.'
    model = OrganizationMember

    def get_context_data(self, **kwargs):
        data = super(OrganizationMembershipList, self).get_context_data(**kwargs)
        data['memberships'] = OrganizationMember.objects.filter(user__isnull=False)
        data['invitations'] = OrganizationMember.objects.filter(user__isnull=True)
        return data


class OrganizationMembershipEdit(OrganizationViewMixin, BitcasterBaseUpdateView):
    # form_class = OrganizationForm
    fields = ('role',)
    # template_name = 'bitcaster/organization/member_edit.html'
    success_url = ''
    model = OrganizationMember

    def get_template_names(self):
        return super().get_template_names()

    def get_context_data(self, **kwargs):
        kwargs['title'] = _('Edit Membership')
        kwargs['membership'] = self.object
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        self.message_user(_('Updated'))
        return super(OrganizationMembershipEdit, self).form_valid(form)

    def get_success_url(self):
        return reverse('org-member-list', args=[self.selected_organization.slug])


class OrganizationMembershipDelete(OrganizationViewMixin, BitcasterBaseDeleteView):
    def get_success_url(self):
        return reverse('org-member-list', args=[self.selected_organization.slug])

    def get_queryset(self):
        return self.selected_organization.memberships.filter(user__isnull=False)

    def delete(self, request, *args, **kwargs):
        ret = super().delete(request, *args, **kwargs)
        self.message_user('Membership removed')
        return ret


# Invitation

class InviteAccept(OrganizationAuditMixin, MessageUserMixin, CreateView):
    model = User
    form_class = UserInviteRegistrationForm
    template_name = 'bitcaster/users/user_welcome.html'

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

    def form_valid(self, form):
        with transaction.atomic():
            user = User.objects.create(email=form.cleaned_data['email'],
                                       is_active=True,
                                       friendly_name=form.cleaned_data['friendly_name'],
                                       password=make_password(form.cleaned_data['password']),
                                       )
            self.membership.user = user
            self.membership.date_enrolled = timezone.now()
            self.membership.save()
            login(self.request, user, backend=fqn(ModelBackend))
            assert self.request.user == user
            self.audit_log(AuditEvent.MEMBER_ACCEPT,
                           role=self.membership.get_role_display(),
                           invited_by=self.membership.invited_by.email)

        if self.membership.role in [Role.OWNER, Role.ADMIN]:
            url = reverse('org-dashboard', args=[self.selected_organization.slug])
        else:
            url = reverse('me-home')
        logger.debug(f'Invitation accepted by user {user.email} with role {self.membership.role}. '
                     f'Redirecting to {url}')
        return HttpResponseRedirect(url)

    def form_invalid(self, form):
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        if self.membership:
            kwargs['membership'] = self.membership
            kwargs['invitation_id'] = self.membership.pk  # this is required by oauth
            return super().get_context_data(**kwargs)
        else:
            return {}

    def get_initial(self):
        return {'email': self.membership.email,
                'friendly_name': self.membership.email}

    @cached_property
    def membership(self):
        pk = self.kwargs['pk']
        return OrganizationMember.objects.filter(pk=pk,
                                                 organization__slug=self.kwargs['org']).first()

    def get(self, request, **kwargs):
        check = kwargs['check']
        if totp.verify(check, valid_window=config.INVITATION_EXPIRE):
            return super(InviteAccept, self).get(request, **kwargs)
        self.message_user(_('Invite expired'), messages.ERROR)
        return HttpResponseRedirect('/')


class InviteSend(OrganizationViewMixin, BitcasterBaseUpdateView):
    fields = ()

    def get_success_url(self):
        return reverse('org-member-list', args=[self.selected_organization.slug])

    def get_queryset(self):
        return self.selected_organization.memberships.all()

    def form_valid(self, form):
        membership = self.get_object()
        try:
            membership.send_email()
            self.message_user(_('Email sending scheduled'))
        except Exception as e:
            logger.exception(e)
            self.message_user(_('Error sending email'), messages.ERROR)
        return super().form_valid(form)


class InviteDelete(SelectedOrganizationMixin, DeleteView):

    def get_success_url(self):
        return reverse('org-member-list', args=[self.selected_organization.slug])

    def get_queryset(self):
        return self.selected_organization.memberships.filter(user__isnull=True)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.delete()
        return HttpResponseRedirect(success_url)


class OrganizationInvite(OrganizationViewMixin, BitcasterFormView):
    form_class = OrganizationInvitationForm
    template_name = 'bitcaster/organization_invite.html'

    def get_success_url(self):
        return reverse('org-member-list', args=[self.selected_organization.slug])

    def get_context_data(self, **kwargs):
        data = super(OrganizationInvite, self).get_context_data(**kwargs)
        data['invitations'] = data['form']
        return data

    def get_form_class(self):
        return OrganizationInvitationFormSet

    def form_invalid(self, form):
        self.message_user(_('invalid'), messages.WARNING)
        return super(OrganizationInvite, self).form_invalid(form)

    def form_valid(self, form):
        sent = False
        form.instance = self.selected_organization
        for inline_form in form.extra_forms:
            if not inline_form.has_changed():
                continue
            recipient = inline_form.cleaned_data.get('email', None)
            if recipient:
                if not self.selected_organization.memberships.filter(email=recipient).exists():
                    inline_form.instance.organization = self.selected_organization
                    inline_form.instance.invited_by = self.request.user
                    membership = inline_form.save()
                    membership.send_email()
                    self.audit_log(AuditEvent.MEMBER_INVITE,
                                   role=membership.get_role_display(),
                                   email=membership.email)
                    sent = True
                else:
                    self.message_user(_('Invitation to {0} already sent').format(recipient),
                                      messages.WARNING)
        if sent:
            self.message_user(_('Invitations sent'), messages.SUCCESS)
        return super(OrganizationInvite, self).form_valid(form)


class OrganizationApplications(OrganizationViewMixin, BitcasterBaseDetailView):
    form_class = OrganizationForm
    template_name = 'bitcaster/organization/organization_applications.html'
    success_url = '.'


# Channels

class OrganizationChannels(OrganizationAuditMixin, ApplicationListMixin, ListView):
    template_name = 'bitcaster/organization_channels.html'

    def get_queryset(self):
        return self.selected_organization.channels.all()

    def get_context_data(self, **kwargs):
        kwargs['channel_context'] = self.selected_organization
        kwargs['title'] = _('Organization Channels')
        kwargs['create_url'] = reverse('org-channel-create',
                                       args=[self.selected_organization.slug])
        return super().get_context_data(**kwargs)


class OrganizationChannelUpdate(OrganizationViewMixin, ChannelUpdateView):
    template_name = 'bitcaster/org_channel_configure.html'

    def get_success_url(self):
        return reverse_lazy('org-channel-list',
                            args=[self.selected_organization.slug])

    def get_queryset(self):
        return self.selected_organization.channels.all()


class OrganizationChannelRemove(OrganizationViewMixin, ChannelDeleteView):
    template_name = 'bitcaster/org_channel_remove.html'

    def get_success_url(self):
        return reverse_lazy('org-channel-list',
                            args=[self.selected_organization.slug])

    def get_queryset(self):
        return self.selected_organization.channels.all()


class OrganizationChannelToggle(OrganizationViewMixin, ChannelToggleView):
    pattern_name = 'org-channel-list'

    def get_queryset(self):
        return self.selected_organization.channels.all()

    def get_redirect_url(self, *args, **kwargs):
        return reverse_lazy('org-channel-list',
                            args=[self.selected_organization.slug])


class OrganizationChannelDeprecate(OrganizationViewMixin, ChannelDeprecateView):
    pattern_name = 'org-channel-list'

    def get_queryset(self):
        return self.selected_organization.channels.all()

    def get_redirect_url(self, *args, **kwargs):
        return reverse_lazy('org-channel-list',
                            args=[self.selected_organization.slug])


class OrganizationChannelCreate(OrganizationViewMixin, ChannelCreateWizard):
    TEMPLATES = {'a': 'bitcaster/org_channel_wizard1.html',
                 'b': 'bitcaster/org_channel_wizard2.html',
                 }

    def get_success_url(self):
        return reverse_lazy('org-channel-list', args=[self.selected_organization.slug])

    def get_extra_instance_kwargs(self):
        return {'organization': self.selected_organization}


# Teams

class OrganizationTeamMixin(OrganizationViewMixin):
    model = Team

    def get_queryset(self):
        return self.selected_organization.teams.all()

    def get_context_data(self, **kwargs):
        kwargs['title'] = _('Organization Teams')
        return super().get_context_data(**kwargs)


class OrganizationTeamList(OrganizationTeamMixin, BitcasterBaseListView):
    pass


class OrganizationTeamCreate(OrganizationTeamMixin, BitcasterBaseCreateView):
    form_class = TeamForm

    def get_success_url(self):
        return reverse('org-team-list', args=[self.selected_organization.slug])

    def get_initial(self):
        return {'manager': self.request.user}

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'organization': self.selected_organization})
        return kwargs

    def form_valid(self, form):
        with transaction.atomic():
            obj = Team.objects.create(
                name=form.cleaned_data['name'],
                manager=form.cleaned_data['manager'],
                organization=self.selected_organization)
            for member in form.cleaned_data['members']:
                TeamMembership.objects.get_or_create(team=obj,
                                                     member=member)

        return HttpResponseRedirect(self.get_success_url())


class OrganizationTeamUpdate(OrganizationTeamMixin, BitcasterBaseUpdateView):
    form_class = TeamForm
    slug_url_kwarg = 'slug'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'organization': self.selected_organization})
        return kwargs

    def get_success_url(self):
        return reverse('org-team-list', args=[self.selected_organization.slug])

    def form_valid(self, form):
        with transaction.atomic():
            obj = self.get_object()
            obj.name = form.cleaned_data['name']
            obj.manager = form.cleaned_data['manager']
            existing = obj.members.all()
            selection = form.cleaned_data['members']
            for member in selection:
                if member not in existing:
                    TeamMembership.objects.get_or_create(team=obj,
                                                         member=member)
            obj.memberships.exclude(member__in=selection).delete()
        return HttpResponseRedirect(self.get_success_url())


class OrganizationTeamMember(OrganizationTeamMixin, UpdateView):
    fields = ('name',)
    slug_url_kwarg = 'slug'

    def get_success_url(self):
        return reverse('org-team-list', args=[self.selected_organization.slug])

    def get_initial(self):
        return super().get_initial()

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.organization = self.selected_organization
        obj.save()
        return HttpResponseRedirect(self.get_success_url())
