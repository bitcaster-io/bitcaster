# -*- coding: utf-8 -*-
import logging

from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import gettext as _

from mercury.models import Organization
from mercury.web.forms import OrganizationForm
from mercury.web.views.base import (MercuryBaseCreateView,
                                    MercuryBaseDetailView,
                                    MercuryBaseUpdateView,)

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


class OrganizationChannels(OrganizationViewMixin, MercuryBaseDetailView):
    form_class = OrganizationForm
    template_name = 'mercury/organization_channels.html'
    success_url = '.'


class OrganizationApplications(OrganizationViewMixin, MercuryBaseDetailView):
    form_class = OrganizationForm
    template_name = 'mercury/organization_applications.html'
    success_url = '.'
