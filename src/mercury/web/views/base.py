# -*- coding: utf-8 -*-
"""
mercury / base
~~~~~~~~~~~~~~~~~

:copyright: (c) 2018 Stefano Apostolico, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

import logging

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.utils.functional import cached_property
from django.views import View
from django.views.generic import TemplateView

from mercury.models import Organization

logger = logging.getLogger(__name__)


@method_decorator(login_required, name='dispatch')
class SecuredViewMixin(View):
    def check_perms(self, request, obj=None, raise_exception=False):
        return request.user.has_perm(obj)


class OrganizationListMixin(SecuredViewMixin):
    def get_context_data(self, **kwargs):
        ret = super().get_context_data(**kwargs)
        ret['organizations'] = Organization.objects.filter(members=self.request.user)
        return ret

class ApplicationListMixin(SecuredViewMixin):
    def get_context_data(self, **kwargs):
        ret = super().get_context_data(**kwargs)
        ret['applications'] = self.selected_organization.applications.all()
        return ret


class SelectedOrganizationMixin(ApplicationListMixin):
    def get_context_data(self, **kwargs):
        kwargs['organization'] = self.selected_organization
        return super().get_context_data(**kwargs)

    @cached_property
    def selected_organization(self):  # returns selected office and caches the office
        organization = Organization.objects.get(slug=self.kwargs['org'])
        self.check_perms(self.request, organization, True)
        return organization


class SelectedApplicationMixin(SelectedOrganizationMixin):
    def get_context_data(self, **kwargs):
        kwargs['application'] = self.selected_application
        return super().get_context_data(**kwargs)

    @cached_property
    def selected_application(self):
        slug = self.kwargs['app']
        app = self.selected_organization.applications.get(slug=slug)
        self.check_perms(self.request, app, True)
        return app


class MercuryTemplateView(ApplicationListMixin, OrganizationListMixin, TemplateView):
    pass
