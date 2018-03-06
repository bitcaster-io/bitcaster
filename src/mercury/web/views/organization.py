# -*- coding: utf-8 -*-
import logging

from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from mercury.models import Organization, OrganizationMember
from mercury.web.forms import (OrganizationForm, OrganizationInviteForm,
                               OrganizationInviteFormSet,)
from mercury.web.views.base import (MercuryBaseCreateView,
                                    MercuryBaseDetailView,
                                    MercuryBaseUpdateView, MercuryFormView,)

logger = logging.getLogger(__name__)

__all__ = ["OrganizationCreate", "OrganizationDetail", "OrganizationUpdate",
           "OrganizationMembers", "OrganizationChannels",
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
        url = reverse("org-config", args=[form.cleaned_data['slug']])
        self.object = form.save()
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
                recipient = inline_form.cleaned_data['email']
                if not inline_form.has_changed():
                    continue
                if not self.selected_organization.memberships.filter(email=recipient).exists():
                    inline_form.instance.organization = self.selected_organization
                    inline_form.save()
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
