# -*- coding: utf-8 -*-
"""
mercury / base
~~~~~~~~~~~~~~~~~

:copyright: (c) 2018 Stefano Apostolico, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator
from django.utils.functional import cached_property
from django.views.generic import (CreateView, DetailView, FormView,
                                  TemplateView, UpdateView,)

from mercury.models import Organization

logger = logging.getLogger(__name__)


class SecuredViewMixin:
    def check_perms(self, request, obj=None, raise_exception=False):
        return request.user.has_perm(obj)

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


@method_decorator(user_passes_test(lambda u: u.is_superuser), name='dispatch')
class SuperuserViewMixin(SecuredViewMixin):
    def check_perms(self, request, obj=None, raise_exception=False):
        return request.user.has_perm(obj)


class OrganizationListMixin(SecuredViewMixin):
    def get_context_data(self, **kwargs):
        ret = super().get_context_data(**kwargs)
        ret['organizations'] = Organization.objects.filter(members=self.request.user)
        return ret


class SelectedOrganizationMixin(OrganizationListMixin):
    def get_context_data(self, **kwargs):
        kwargs['organization'] = self.selected_organization
        return super().get_context_data(**kwargs)

    @cached_property
    def selected_organization(self):  # returns selected office and caches the office
        if 'org' not in self.kwargs:
            return None
        organization = Organization.objects.get(slug=self.kwargs['org'])
        self.check_perms(self.request, organization, True)
        return organization


class ApplicationListMixin(SelectedOrganizationMixin):
    def get_context_data(self, **kwargs):
        ret = super().get_context_data(**kwargs)
        if self.selected_organization:
            ret['applications'] = self.selected_organization.applications.all()
        else:
            ret['applications'] = None
        return ret


class SelectedApplicationMixin(ApplicationListMixin):
    def get_context_data(self, **kwargs):
        kwargs['application'] = self.selected_application
        return super().get_context_data(**kwargs)

    @cached_property
    def selected_application(self):
        if self.selected_organization and 'app' in self.kwargs:
            slug = self.kwargs['app']
            app = self.selected_organization.applications.get(slug=slug)
            self.check_perms(self.request, app, True)
            return app
        return None


class MessageUserMixin(object):
    def message_user(self, message, level=messages.SUCCESS, extra_tags='',
                     fail_silently=False):
        messages.add_message(self.request, level, message, extra_tags=extra_tags, fail_silently=fail_silently)


class MercuryTemplateView(ApplicationListMixin,
                          OrganizationListMixin,
                          MessageUserMixin,
                          TemplateView):
    pass


class MercuryFormView(ApplicationListMixin,
                      MessageUserMixin,
                      OrganizationListMixin,
                      FormView):
    pass


class MercuryBaseViewMixin(MessageUserMixin, ApplicationListMixin):
    pass


class MercuryBaseCreateView(MercuryBaseViewMixin, CreateView):
    pass


class MercuryBaseUpdateView(MercuryBaseViewMixin, UpdateView):
    pass


class MercuryBaseDetailView(MercuryBaseViewMixin, DetailView):
    pass
