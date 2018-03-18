# -*- coding: utf-8 -*-
import logging

from django.contrib import messages
from django.core.cache import cache
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext as _
from django.views.generic import DetailView, ListView
from rest_framework.exceptions import PermissionDenied

from bitcaster.models import Application
from bitcaster.security import is_owner
from bitcaster.utils.dashboard import check_channels, check_events
from bitcaster.web.forms import ApplicationCreateForm
from bitcaster.web.views.base import (BitcasterBaseCreateView,
                                      BitcasterBaseDetailView,
                                      SelectedApplicationMixin,)

from .channel import (ChannelCreateWizard, ChannelDeleteView,
                      ChannelDeprecateView,
                      ChannelToggleView, ChannelUpdateView,)

logger = logging.getLogger(__name__)

__all__ = ["ApplicationCreate",
           "ApplicationDetail",
           "ApplicationChannels",
           "ApplicationChannelUpdate",
           "ApplicationChannelToggle",
           "ApplicationChannelRemove",
           "ApplicationChannelDeprecate",
           "ApplicationChannelCreate",
           "ApplicationDashboard"
           ]


class ApplicationViewMixin(SelectedApplicationMixin):
    model = Application
    slug_url_kwarg = 'app'

    def dispatch(self, request, *args, **kwargs):
        if not is_owner(request.user, self.selected_application):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class ApplicationDashboard(ApplicationViewMixin, BitcasterBaseDetailView):
    template_name = 'bitcaster/application_dashboard.html'

    def get_context_data(self, **kwargs):
        app = self.get_object()
        cache_key = f"org:app:dashboard:{app.pk}"
        org_data = cache.get(cache_key)
        if not org_data:
            org_data = {
                # "active_users": org.members.count(),
                # "pending_users": org.invitations.count(),
                "enabled_channels": app.channels.filter(enabled=True).count(),
                "disabled_channels": app.channels.filter(enabled=False).count(),
                "enabled_events": app.events.filter(enabled=True).count(),
                "disabled_events": app.events.filter(enabled=False).count(),
            }
            org_data["box_channels"] = check_channels(org_data)
            org_data["box_events"] = check_events(org_data)
            # cache.set(cache_key, org_data)
        kwargs['data'] = org_data
        return super().get_context_data(**kwargs)


class ApplicationCreate(BitcasterBaseCreateView):
    model = Application
    form_class = ApplicationCreateForm

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
        return reverse_lazy("app-channel-list",
                            args=[self.selected_organization.slug,
                                  self.selected_application.slug])


class ApplicationChannels(ApplicationViewMixin,
                          ChannelViewMixin, ListView):
    template_name = 'bitcaster/application_channels.html'

    def get_queryset(self):
        return self.selected_application.channels.all()

    def get_context_data(self, **kwargs):
        kwargs['channel_context'] = self.selected_application
        kwargs['title'] = _("Application Channels")
        kwargs['create_url'] = reverse("app-channel-create",
                                       args=[self.selected_organization.slug,
                                             self.selected_application.slug,
                                             ])
        return super().get_context_data(**kwargs)


class ApplicationChannelUpdate(ApplicationViewMixin, ChannelViewMixin,
                               ChannelUpdateView):
    template_name = 'bitcaster/app_channel_configure.html'

    def get_queryset(self):
        return self.selected_application.channels.filter(system=False,
                                                         application=self)

    def get_extra_instance_kwargs(self):
        return {'organization': self.selected_organization,
                'application': self.selected_application}


class ApplicationChannelRemove(ApplicationViewMixin, ChannelDeleteView):
    template_name = 'bitcaster/app_channel_remove.html'

    def get_queryset(self):
        return self.selected_application.channels.filter(system=False,
                                                         application=self)


class ApplicationChannelToggle(ApplicationViewMixin, ChannelViewMixin,
                               ChannelToggleView):
    pattern_name = 'app-channel-list'

    def get_queryset(self):
        return self.selected_application.channels.filter(system=False,
                                                         application=self.selected_application)

    def get_redirect_url(self, *args, **kwargs):
        return reverse_lazy("app-channel-list",
                            args=[self.selected_organization.slug,
                                  self.selected_application.slug])


class ApplicationChannelDeprecate(ApplicationViewMixin, ChannelViewMixin, ChannelDeprecateView):
    pattern_name = 'app-channel-list'


class ApplicationChannelCreate(ApplicationViewMixin, ChannelCreateWizard):
    TEMPLATES = {"a": "bitcaster/app_channel_wizard1.html",
                 "b": "bitcaster/app_channel_wizard2.html",
                 }

    def get_extra_instance_kwargs(self):
        return {'organization': self.selected_organization,
                'application': self.selected_application}

    def get_success_url(self):
        return reverse_lazy("app-channel-list",
                            args=[self.selected_organization.slug,
                                  self.selected_application.slug])
