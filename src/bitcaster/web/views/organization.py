# -*- coding: utf-8 -*-
import logging

from constance import config
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.hashers import make_password
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.http import Http404, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from django.views.generic import CreateView, DeleteView, ListView
from strategy_field.utils import fqn

from bitcaster.models import Organization, OrganizationMember, Team, User
from bitcaster.otp import totp
from bitcaster.security import is_owner
from bitcaster.web.forms import (OrganizationForm, OrganizationInvitationForm,
                                 OrganizationInvitationFormSet,
                                 UserInviteRegistrationForm, )

from .base import (BitcasterBaseCreateView, BitcasterBaseDetailView,
                   BitcasterBaseListView, BitcasterBaseUpdateView, BitcasterFormView,
                   MessageUserMixin, SelectedOrganizationMixin, )
from .channel import (ChannelCreateWizard, ChannelDeleteView,
                      ChannelDeprecateView, ChannelListView,
                      ChannelToggleView, ChannelUpdateView, )

logger = logging.getLogger(__name__)

__all__ = ["OrganizationCreate", "OrganizationDetail", "OrganizationUpdate",
           "OrganizationMembers", "OrganizationChannels",
           "OrganizationTeamList", "OrganizationTeamCreate",
           "OrganizationChannelRemove", "OrganizationChannelToggle",
           "OrganizationChannelUpdate", "OrganizationChannelDeprecate",
           "OrganizationInvite", "InviteDelete", "InviteSend", "InviteAccept",
           "OrganizationApplications", "OrganizationChannelCreate"]


class OrganizationViewMixin(SelectedOrganizationMixin):
    model = Organization
    slug_url_kwarg = 'org'

    def dispatch(self, request, *args, **kwargs):
        if not is_owner(request.user, self.selected_organization):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class OrganizationDetail(OrganizationViewMixin, BitcasterBaseDetailView):

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)


class OrganizationUpdate(OrganizationViewMixin, BitcasterBaseUpdateView):
    form_class = OrganizationForm
    success_url = '.'

    def form_valid(self, form):
        slug = form.cleaned_data.get('slug', None)
        self.object = form.save()
        url = reverse("org-config", args=[slug or self.object.slug])
        self.message_user(_("Configuration saved"))
        return HttpResponseRedirect(url)


class OrganizationCreate(OrganizationViewMixin, BitcasterBaseCreateView):
    form_class = OrganizationForm
    success_url = '.'

    def form_valid(self, form):
        form.instance.owner = self.request.user
        self.message_user(_('Organization created'), messages.SUCCESS)
        return super().form_valid(form)


class OrganizationMembers(OrganizationViewMixin, BitcasterBaseDetailView):
    form_class = OrganizationForm
    template_name = 'bitcaster/organization_members.html'
    success_url = '.'

    def get_context_data(self, **kwargs):
        data = super(OrganizationMembers, self).get_context_data(**kwargs)
        data['memberships'] = OrganizationMember.objects.filter(user__isnull=False)
        data['invitations'] = OrganizationMember.objects.filter(user__isnull=True)
        return data


# Invitation

class InviteAccept(SelectedOrganizationMixin, MessageUserMixin, CreateView):
    model = User
    form_class = UserInviteRegistrationForm
    template_name = 'bitcaster/users/user_welcome.html'

    def check_perms(self, *args, **kwargs):
        return True

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            raise Http404
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        with transaction.atomic():
            user = User.objects.create(email=form.cleaned_data['email'],
                                       is_active=True,
                                       friendly_name=form.cleaned_data['friendly_name'],
                                       password=make_password(form.cleaned_data['password']),
                                       )
            self.membership.user = user
            self.membership.save()
            login(self.request, user, backend=fqn(ModelBackend))
        url = reverse('org-index', args=[self.selected_organization.slug])
        return HttpResponseRedirect(url)

    def form_invalid(self, form):
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        kwargs['membership'] = self.membership
        kwargs['invitation_id'] = self.membership.pk  # this is required by oauth
        return super().get_context_data(**kwargs)

    def get_initial(self):
        return {"email": self.membership.email}

    @cached_property
    def membership(self):
        pk = self.kwargs['pk']
        return OrganizationMember.objects.get(pk=pk)

    def get(self, request, **kwargs):
        check = kwargs['check']
        if totp.verify(check, valid_window=config.INVITATION_EXPIRE):
            return super(InviteAccept, self).get(request, **kwargs)

        self.message_user("Invite expired", messages.ERROR)
        return HttpResponseRedirect("/")


class InviteSend(OrganizationViewMixin, BitcasterBaseUpdateView):
    fields = ()

    def get_success_url(self):
        return reverse("org-members", args=[self.selected_organization.slug])

    def get_queryset(self):
        return self.selected_organization.memberships.all()

    def form_valid(self, form):
        membership = self.get_object()
        membership.send_email()
        self.message_user(_("Email sending scheduled"))
        return super().form_valid(form)


class InviteDelete(SelectedOrganizationMixin, DeleteView):

    def get_success_url(self):
        return reverse("org-members", args=[self.selected_organization.slug])

    def get_queryset(self):
        return self.selected_organization.memberships.all()

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.delete()
        return HttpResponseRedirect(success_url)


class OrganizationInvite(BitcasterFormView):
    form_class = OrganizationInvitationForm
    template_name = 'bitcaster/organization_invite.html'

    def get_success_url(self):
        return reverse("org-members", args=[self.selected_organization.slug])

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
        if form.is_valid():
            form.instance = self.selected_organization
            for inline_form in form.extra_forms:
                if not inline_form.has_changed():
                    continue
                recipient = inline_form.cleaned_data.get('email', None)
                if recipient:
                    if not self.selected_organization.memberships.filter(email=recipient).exists():
                        inline_form.instance.organization = self.selected_organization
                        membership = inline_form.save()
                        membership.send_email()
                        sent = True
                    else:
                        self.message_user(_('Invitation to {0} already sent').format(recipient),
                                          messages.WARNING)
            if sent:
                self.message_user(_('Invitations sent'), messages.SUCCESS)
        return super(OrganizationInvite, self).form_valid(form)


class OrganizationApplications(OrganizationViewMixin, BitcasterBaseDetailView):
    form_class = OrganizationForm
    template_name = 'bitcaster/organization_applications.html'
    success_url = '.'


# Channels

class OrganizationChannels(OrganizationViewMixin, ChannelListView):
    template_name = 'bitcaster/organization_channels.html'

    def get_queryset(self):
        return self.selected_organization.channels.all()

    def get_context_data(self, **kwargs):
        kwargs['title'] = _("Organization Channels")
        kwargs['create_url'] = reverse("org-channel-create",
                                       args=[self.selected_organization.slug])
        return super().get_context_data(**kwargs)


class OrganizationChannelUpdate(OrganizationViewMixin, ChannelUpdateView):
    template_name = 'bitcaster/org_channel_configure.html'

    def get_success_url(self):
        return reverse_lazy("org-channels",
                            args=[self.selected_organization.slug])

    def get_queryset(self):
        return self.selected_organization.channels.all()


class OrganizationChannelRemove(OrganizationViewMixin, ChannelDeleteView):
    template_name = 'bitcaster/org_channel_remove.html'

    def get_success_url(self):
        return reverse_lazy("org-channels",
                            args=[self.selected_organization.slug])

    def get_queryset(self):
        return self.selected_organization.channels.all()


class OrganizationChannelToggle(OrganizationViewMixin, ChannelToggleView):
    pattern_name = 'org-channels'

    def get_queryset(self):
        return self.selected_organization.channels.all()

    def get_redirect_url(self, *args, **kwargs):
        return reverse_lazy("org-channels",
                            args=[self.selected_organization.slug])


class OrganizationChannelDeprecate(OrganizationViewMixin, ChannelDeprecateView):
    pattern_name = 'org-channels'

    def get_queryset(self):
        return self.selected_organization.channels.all()

    def get_redirect_url(self, *args, **kwargs):
        return reverse_lazy("org-channels",
                            args=[self.selected_organization.slug])


class OrganizationChannelCreate(OrganizationViewMixin, ChannelCreateWizard):
    TEMPLATES = {"a": "bitcaster/org_channel_wizard1.html",
                 "b": "bitcaster/org_channel_wizard2.html",
                 }

    def get_success_url(self):
        return reverse_lazy('org-channels', args=[self.selected_organization.slug])

    def get_extra_instance_kwargs(self):
        return {'organization': self.selected_organization}


# Teams

class OrganizationTeamMixin(OrganizationViewMixin):
    model = Team

    def get_queryset(self):
        return self.selected_organization.teams.all()

    def get_context_data(self, **kwargs):
        kwargs['title'] = _("Organization Teams")
        # kwargs['create_url'] = reverse("org-team-add",
        #                                args=[self.selected_organization.slug])
        return super().get_context_data(**kwargs)


class OrganizationTeamList(OrganizationTeamMixin, ListView):
    pass
    # template_name = 'bitcaster/organization_teams.html'


class OrganizationTeamCreate(OrganizationTeamMixin, CreateView):
    # template_name = 'bitcaster/organization_teams.html'
    fields = ('name',)
