# -*- coding: utf-8 -*-
import logging

from constance import config
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.views.generic import DeleteView, CreateView

from mercury.models import Organization, OrganizationMember, User
from mercury.security import totp
from mercury.web.forms import (OrganizationForm, OrganizationInviteForm,
                               OrganizationInviteFormSet, UserInvitationForm)
from mercury.web.views.base import (MercuryBaseCreateView,
                                    MercuryBaseDetailView,
                                    MercuryBaseUpdateView, MercuryFormView, SelectedOrganizationMixin, MessageUserMixin)

logger = logging.getLogger(__name__)

__all__ = ["OrganizationCreate", "OrganizationDetail", "OrganizationUpdate",
           "OrganizationMembers", "OrganizationChannels",
           "OrganizationInvite", "InviteDelete", "InviteSend", "InviteAccept",
           "OrganizationApplications"]


class OrganizationViewMixin:
    model = Organization
    slug_url_kwarg = 'org'


class OrganizationDetail(OrganizationViewMixin, MercuryBaseDetailView):
    pass


class OrganizationUpdate(OrganizationViewMixin, MercuryBaseUpdateView):
    form_class = OrganizationForm
    success_url = '.'

    def form_valid(self, form):
        slug = form.cleaned_data.get('slug', None)
        self.object = form.save()
        url = reverse("org-config", args=[slug or self.object.slug])
        self.message_user(_("Configuration saved"))
        return HttpResponseRedirect(url)


class OrganizationCreate(OrganizationViewMixin, MercuryBaseCreateView):
    form_class = OrganizationForm
    success_url = '.'

    def form_valid(self, form):
        form.instance.owner = self.request.user
        self.message_user(_('Organization created'), messages.SUCCESS)
        return super().form_valid(form)


class OrganizationMembers(OrganizationViewMixin, MercuryBaseDetailView):
    form_class = OrganizationForm
    template_name = 'mercury/organization_members.html'
    success_url = '.'

    def get_context_data(self, **kwargs):
        data = super(OrganizationMembers, self).get_context_data(**kwargs)
        data['memberships'] = OrganizationMember.objects.filter(user__isnull=False)
        data['invitations'] = OrganizationMember.objects.filter(user__isnull=True)
        return data


class InviteAccept(MessageUserMixin, CreateView):
    model = User
    form_class = UserInvitationForm
    template_name = 'bitcaster/users/user_welcome.html'
    membership = None

    def form_valid(self, form):
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        kwargs['invitation_id'] = self.membership.pk
        return super().get_context_data(**kwargs)

    def get_initial(self):
        if self.membership:
            return {"email": self.membership.email}
        return {}

    def get(self, request, **kwargs):
        check = kwargs['check']
        pk = kwargs['pk']
        if totp.verify(check, valid_window=config.INVITATION_EXPIRE):
            self.membership = OrganizationMember.objects.get(pk=pk)
            return super(InviteAccept, self).get(request, **kwargs)

        self.message_user("Invite expired", messages.ERROR)
        return HttpResponseRedirect("/")


class InviteSend(OrganizationViewMixin, MercuryBaseUpdateView):
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


class OrganizationInvite(MercuryFormView):
    form_class = OrganizationInviteForm
    template_name = 'mercury/organization_invite.html'

    def get_success_url(self):
        return reverse("org-members", args=[self.selected_organization.slug])

    def get_context_data(self, **kwargs):
        data = super(OrganizationInvite, self).get_context_data(**kwargs)
        data['invitations'] = data['form']
        return data

    def get_form_class(self):
        return OrganizationInviteFormSet

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


class OrganizationChannels(OrganizationViewMixin, MercuryBaseDetailView):
    form_class = OrganizationForm
    template_name = 'mercury/organization_channels.html'
    success_url = '.'


class OrganizationApplications(OrganizationViewMixin, MercuryBaseDetailView):
    form_class = OrganizationForm
    template_name = 'mercury/organization_applications.html'
    success_url = '.'
