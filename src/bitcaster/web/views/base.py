# -*- coding: utf-8 -*-
import logging

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.http import Http404
from django.utils.decorators import method_decorator
from django.utils.functional import cached_property
from django.views.generic import (CreateView, DeleteView, DetailView, FormView,
                                  ListView, TemplateView, UpdateView,)
from django.views.generic.base import TemplateResponseMixin
from strategy_field.utils import import_by_name

from bitcaster import messages
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
        ret['organizations'] = Organization.objects.filter(members=self.request.user)
        return ret


class SelectedOrganizationMixin(SecuredViewMixin):

    def get_context_data(self, **kwargs):
        kwargs['organizations'] = Organization.objects.filter(members=self.request.user)
        if self.selected_organization:
            kwargs['organizations'] = kwargs['organizations'].exclude(id=self.selected_organization.id)

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
            try:
                app = self.selected_organization.applications.get(slug=slug)
                self.check_perms(self.request, app, True)
            except Application.DoesNotExist:
                raise Http404
            return app
        return None


class MessageUserMixin:
    def alarm(self, message, level=messages.ERROR, extra_tags='',
              fail_silently=False):
        messages.add_alarm(self.request, level, message,
                           extra_tags=extra_tags,
                           fail_silently=fail_silently)

    def message_user(self, message, level=messages.INFO, extra_tags='',
                     fail_silently=False):
        messages.add_message(self.request, level, message,
                             extra_tags=extra_tags,
                             fail_silently=fail_silently)


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


class BitcasterSingleObjectTemplateResponseMixin(TemplateResponseMixin):
    template_name_base = None

    def get_template_names(self):
        try:
            if self.template_name is None:
                raise ImproperlyConfigured(
                    'TemplateResponseMixin requires either a definition of '
                    "'template_name' or an implementation of 'get_template_names()'")
            names = [self.template_name]
        except ImproperlyConfigured:
            names = []

            # If self.template_name_field is set, grab the value of the field
            # of that name from the object; this is the most specific template
            # name, if given.
            if self.object and self.template_name_field:
                name = getattr(self.object, self.template_name_field, None)
                if name:
                    names.insert(0, name)

            if self.template_name_base:
                base = 'bitcaster/%s' % self.template_name_base
            else:
                base = 'bitcaster'

            # The least-specific option is the default <app>/<model>_detail.html;
            # only use this if the object in question is a model.
            if isinstance(self.object, models.Model):
                object_meta = self.object._meta
                names.append('%s/%s%s.html' % (
                    base,
                    object_meta.model_name,
                    self.template_name_suffix
                ))
            elif getattr(self, 'model', None) is not None and issubclass(self.model, models.Model):
                names.append('%s/%s%s.html' % (
                    base,
                    self.model._meta.model_name,
                    self.template_name_suffix
                ))

            # If we still haven't managed to find any template names, we should
            # re-raise the ImproperlyConfigured to alert the user.
            if not names:
                raise

        return names


class BitcasterBaseListView(BitcasterBaseViewMixin, ListView):
    template_name_base = None

    def get_template_names(self):
        names = []
        if self.template_name:
            names = [self.template_name]

        if hasattr(self.object_list, 'model'):
            opts = self.object_list.model._meta
            names.append('%s/%s/%s%s.html' % (opts.app_label,
                                              self.template_name_base,
                                              opts.model_name,
                                              self.template_name_suffix))
        elif not names:
            raise ImproperlyConfigured(
                "%(cls)s requires either a 'template_name' attribute "
                'or a get_queryset() method that returns a QuerySet.' % {
                    'cls': self.__class__.__name__,
                }
            )
        return names


class BitcasterBaseCreateView(BitcasterBaseViewMixin, BitcasterSingleObjectTemplateResponseMixin, CreateView):
    pass


class BitcasterBaseUpdateView(BitcasterBaseViewMixin, BitcasterSingleObjectTemplateResponseMixin, UpdateView):
    template_name_suffix = '_edit'


class BitcasterBaseDeleteView(BitcasterBaseViewMixin, BitcasterSingleObjectTemplateResponseMixin, DeleteView):
    pass


class BitcasterBaseDetailView(BitcasterBaseViewMixin, BitcasterSingleObjectTemplateResponseMixin, DetailView):
    pass


class PluginInfo(BitcasterTemplateView):
    template_name = 'bitcaster/plugin_info.html'

    def get_context_data(self, **kwargs):
        handler = import_by_name(self.kwargs['fqn'])
        return super().get_context_data(handler=handler, **kwargs)

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
