# -*- coding: utf-8 -*-
import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.utils.decorators import method_decorator
from django.utils.functional import cached_property
from django.views.generic import (CreateView, DeleteView, DetailView, FormView,
                                  ListView, TemplateView, UpdateView,)
from strategy_field.utils import import_by_name

from bitcaster.models import Application, Organization
from bitcaster.security import authorized_or_403

logger = logging.getLogger(__name__)


class SecuredViewMixin:
    def check_perms(self, request, obj=None, raise_exception=False):
        return request.user.has_perm('', obj)

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


@method_decorator(authorized_or_403(lambda u: u.is_superuser), name='dispatch')
class SuperuserViewMixin(SecuredViewMixin):
    def check_perms(self, request, obj=None, raise_exception=False):
        return request.user.has_perm(obj)


class OrganizationListMixin(SecuredViewMixin):
    def get_context_data(self, **kwargs):
        ret = super().get_context_data(**kwargs)
        if not settings.ON_PREMISE:
            ret['organizations'] = Organization.objects.filter(members=self.request.user)
        return ret


class SelectedOrganizationMixin(SecuredViewMixin):
    def get_context_data(self, **kwargs):
        kwargs['organization'] = self.selected_organization
        return super().get_context_data(**kwargs)

    @cached_property
    def selected_organization(self):  # returns selected office and caches the office
        if 'org' not in self.kwargs:
            return None
        try:
            organization = Organization.objects.get(slug=self.kwargs['org'])
            self.check_perms(self.request, organization, True)
        except Organization.DoesNotExist:
            raise Http404
        return organization


class ApplicationListMixin(SelectedOrganizationMixin, OrganizationListMixin):
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
            try:
                app = self.selected_organization.applications.get(slug=slug)
                self.check_perms(self.request, app, True)
            except Application.DoesNotExist:
                raise Http404
            return app
        return None


class MessageUserMixin:
    def message_user(self, message, level=messages.INFO, extra_tags='',
                     fail_silently=False):
        messages.add_message(self.request, level, message, extra_tags=extra_tags, fail_silently=fail_silently)


class BitcasterTemplateView(ApplicationListMixin,
                          OrganizationListMixin,
                          MessageUserMixin,
                          TemplateView):
    pass


class BitcasterFormView(ApplicationListMixin,
                      MessageUserMixin,
                      OrganizationListMixin,
                      FormView):
    pass


class BitcasterBaseViewMixin(MessageUserMixin, ApplicationListMixin):
    pass


class BitcasterBaseCreateView(BitcasterBaseViewMixin, CreateView):
    pass


class BitcasterBaseListView(BitcasterBaseViewMixin, ListView):
    pass


class BitcasterBaseUpdateView(BitcasterBaseViewMixin, UpdateView):
    pass


class BitcasterBaseDeleteView(BitcasterBaseViewMixin, DeleteView):
    pass


class BitcasterBaseDetailView(BitcasterBaseViewMixin, DetailView):
    pass


class PluginInfo(BitcasterTemplateView):
    template_name = 'bitcaster/plugin_info.html'

    def get_context_data(self, **kwargs):
        handler = import_by_name(self.kwargs['fqn'])
        return super().get_context_data(handler=handler, **kwargs)

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
