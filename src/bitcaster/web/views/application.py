# -*- coding: utf-8 -*-
import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, ListView, RedirectView

from bitcaster.models import Application, ApplicationTriggerKey, Subscription
from bitcaster.models.configurationissue import check_application
from bitcaster.web.forms import (ApplicationCreateForm, ApplicationForm,
                                 ApplicationTriggerKeyForm,)
from bitcaster.web.views.base import (BitcasterBaseCreateView,
                                      BitcasterBaseDeleteView,
                                      BitcasterBaseDetailView,
                                      BitcasterBaseListView,
                                      BitcasterBaseUpdateView,
                                      SelectedApplicationMixin,)

logger = logging.getLogger(__name__)

__all__ = ['ApplicationCreate',
           'ApplicationDetail',
           # 'ApplicationChannels',
           'ApplicationCheckConfigView',
           'ApplicationKeyCreate',
           'ApplicationKeyDelete',
           'ApplicationKeyList',
           'ApplicationKeyUpdate',
           'ApplicationUpdateView',
           # 'ApplicationChannelUpdate',
           # 'ApplicationChannelToggle',
           # 'ApplicationChannelRemove',
           # 'ApplicationChannelDeprecate',
           # 'ApplicationChannelCreate',
           'ApplicationDashboard',
           'ApplicationSubscriptionList',

           ]


class ApplicationViewMixin(SelectedApplicationMixin):
    model = Application
    slug_url_kwarg = 'app'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseRedirect('/')
        if not request.user.has_perm('app:configure', self.selected_application):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class ApplicationUpdateView(ApplicationViewMixin, BitcasterBaseUpdateView):
    model = Application
    form_class = ApplicationForm
    template_name = 'bitcaster/application/form.html'

    def get_context_data(self, **kwargs):
        kwargs['title'] = _('Condigure Application')
        return super().get_context_data(**kwargs)

    def get_success_url(self):
        return reverse('app-dashboard', args=[self.selected_organization.slug,
                                              self.object.slug])


class ApplicationDashboard(ApplicationViewMixin, BitcasterBaseDetailView):
    template_name = 'bitcaster/application/dashboard.html'

    def get_context_data(self, **kwargs):
        app = self.get_object()
        cache_key = f'org:app:dashboard:{app.pk}'
        org_data = cache.get(cache_key, version=app.version)
        if not org_data:
            org_data = {
                # "active_users": org.members.count(),
                # "pending_users": org.invitations.count(),
                'enabled_channels': app.channels.filter(enabled=True).count(),
                'disabled_channels': app.channels.filter(enabled=False).count(),
                'enabled_events': app.events.filter(enabled=True).count(),
                'disabled_events': app.events.filter(enabled=False).count(),
                'enabled_keys': app.keys.filter(enabled=True).count(),
                'disabled_keys': app.keys.filter(enabled=False).count(),
                'access_all_events_keys': app.keys.filter(all_events=True).count(),
            }
            org_data['box_channels'] = app.issues.get_tag_for('channels')
            org_data['box_events'] = app.issues.get_tag_for('events')
            org_data['box_keys'] = app.issues.get_tag_for('keys')
            # cache.set(cache_key, org_data)
        kwargs['data'] = org_data
        return super().get_context_data(**kwargs)


class ApplicationCheckConfigView(ApplicationViewMixin, RedirectView):
    pattern_name = 'app-dashboard'

    def get(self, request, *args, **kwargs):
        check_application(self.selected_application)
        return super().get(request, *args, **kwargs)


class ApplicationCreate(BitcasterBaseCreateView):
    model = Application
    form_class = ApplicationCreateForm
    template_name = 'bitcaster/application/form.html'

    def get_context_data(self, **kwargs):
        kwargs['title'] = _('Create New Application')
        return super().get_context_data(**kwargs)

    def get_success_url(self):
        return reverse('app-dashboard', args=[self.selected_organization.slug,
                                              self.object.slug])

    def form_valid(self, form):
        form.instance.organization = self.selected_organization
        form.instance.owner = self.request.user
        self.message_user(_('Application created'), messages.SUCCESS)
        return super().form_valid(form)


class ApplicationDetail(ApplicationViewMixin, DetailView):
    pass


# Channels
class ChannelViewMixin:
    def get_success_url(self):
        return reverse_lazy('app-channel-list',
                            args=[self.selected_organization.slug,
                                  self.selected_application.slug])


# class ApplicationChannels(ApplicationViewMixin,
#                           ChannelViewMixin, ListView):
#     template_name = 'bitcaster/application_channels.html'
#
#     def get_queryset(self):
#         return self.selected_application.channels.all()
#
#     def get_context_data(self, **kwargs):
#         kwargs['channel_context'] = self.selected_application
#         kwargs['title'] = _('Application Channels')
#         kwargs['create_url'] = reverse('app-channel-create',
#                                        args=[self.selected_organization.slug,
#                                              self.selected_application.slug,
#                                              ])
#         return super().get_context_data(**kwargs)
#
#
# class ApplicationChannelUpdate(ApplicationViewMixin, ChannelViewMixin,
#                                ChannelUpdateView):
#     template_name = 'bitcaster/app_channel_configure.html'
#
#     def get_queryset(self):
#         return self.selected_application.channels.filter(system=False,
#                                                          application=self)
#
#     def get_extra_instance_kwargs(self):
#         return {'organization': self.selected_organization,
#                 'application': self.selected_application}
#
#
# class ApplicationChannelRemove(ApplicationViewMixin, ChannelDeleteView):
#     template_name = 'bitcaster/app_channel_remove.html'
#
#     def get_queryset(self):
#         return self.selected_application.channels.filter(system=False,
#                                                          application=self)
#
#
# class ApplicationChannelToggle(ApplicationViewMixin, ChannelViewMixin,
#                                ChannelToggleView):
#     pattern_name = 'app-channel-list'
#
#     def get_queryset(self):
#         return self.selected_application.channels.filter(system=False,
#                                                          application=self.selected_application)
#
#     def get_redirect_url(self, *args, **kwargs):
#         return reverse_lazy('app-channel-list',
#                             args=[self.selected_organization.slug,
#                                   self.selected_application.slug])
#
#
# class ApplicationChannelDeprecate(ApplicationViewMixin, ChannelViewMixin, ChannelDeprecateView):
#     pattern_name = 'app-channel-list'
#
#
# class ApplicationChannelCreate(ApplicationViewMixin, ChannelCreateWizard):
#     TEMPLATES = {'a': 'bitcaster/app_channel_wizard1.html',
#                  'b': 'bitcaster/app_channel_wizard2.html',
#                  }
#
#     def get_extra_instance_kwargs(self):
#         return {'organization': self.selected_organization,
#                 'application': self.selected_application}
#
#     def get_success_url(self):
#         return reverse_lazy('app-channel-list',
#                             args=[self.selected_organization.slug,
#                                   self.selected_application.slug])


class ApplicationKeyList(ApplicationViewMixin, BitcasterBaseListView):
    template_name = 'bitcaster/application/keys/list.html'

    def get_queryset(self):
        return self.selected_application.keys.all()

    def get_context_data(self, **kwargs):
        kwargs['title'] = _('Application Keys')
        return super().get_context_data(**kwargs)


class ApplicationKeyFormMixin:
    form_class = ApplicationTriggerKeyForm
    model = ApplicationTriggerKey
    template_name = 'bitcaster/application/keys/form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'application': self.selected_application})
        return kwargs

    def get_success_url(self):
        return reverse('app-key-list', args=[self.selected_organization.slug,
                                             self.selected_application.slug])


class ApplicationKeyCreate(ApplicationKeyFormMixin, ApplicationViewMixin,
                           BitcasterBaseCreateView):
    pass


class ApplicationKeyUpdate(ApplicationViewMixin, ApplicationKeyFormMixin, BitcasterBaseUpdateView):

    def get_queryset(self):
        return self.selected_application.keys.all()

    def get_context_data(self, **kwargs):
        kwargs['title'] = _('Application Keys')
        return super().get_context_data(**kwargs)


class ApplicationKeyDelete(ApplicationViewMixin, BitcasterBaseDeleteView):
    pk_url_kwarg = 'pk'
    template_name = 'bitcaster/application/keys/confirm_delete.html'

    def get_object(self, queryset=None):
        return self.selected_application.keys.get(pk=self.kwargs.get(self.pk_url_kwarg))

    def get_success_url(self):
        return reverse('app-key-list', args=[self.selected_organization.slug,
                                             self.selected_application.slug])


class ApplicationSubscriptionList(SelectedApplicationMixin, ListView):
    model = Subscription
    template_name = 'bitcaster/application/subscriptions/list.html'

    def get_context_data(self, **kwargs):
        kwargs['pending'] = self.selected_organization.memberships.filter(event__application=self.selected_application)
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        return Subscription.objects.filter(event__application=self.selected_application)
