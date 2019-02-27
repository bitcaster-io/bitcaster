# -*- coding: utf-8 -*-
import logging

from django.contrib import messages
from django.core.cache import cache
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.views.generic import RedirectView

from bitcaster.models.configurationissue import (check_application,
                                                 check_organization,)
from bitcaster.utils.dashboard import check_channels, get_status
from bitcaster.web.forms import OrganizationForm

from ..base import BitcasterBaseDetailView, BitcasterBaseUpdateView
from .mixins import OrganizationAuditMixin, OrganizationViewMixin

logger = logging.getLogger(__name__)


class OrganizationDashboard(OrganizationViewMixin, BitcasterBaseDetailView):
    template_name = 'bitcaster/organization/dashboard.html'

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


class OrganizationConfiguration(OrganizationViewMixin, BitcasterBaseUpdateView):
    form_class = OrganizationForm
    success_url = '.'
    template_name = 'bitcaster/organization/configuration.html'

    def form_valid(self, form):
        slug = form.cleaned_data.get('slug', None)
        self.object = form.save()
        url = reverse('org-config', args=[slug or self.object.slug])
        self.message_user(_('Configuration saved'), messages.SUCCESS)
        return HttpResponseRedirect(url)


class OrganizationCheckConfigView(OrganizationAuditMixin, RedirectView):
    pattern_name = 'org-dashboard'

    def get(self, request, *args, **kwargs):
        check_organization(self.selected_organization)
        for app in self.selected_organization.applications.all():
            check_application(app)
        return super().get(request, *args, **kwargs)


class OrganizationApplications(OrganizationViewMixin, BitcasterBaseDetailView):
    form_class = OrganizationForm
    template_name = 'bitcaster/organization/organization_applications.html'
    success_url = '.'
