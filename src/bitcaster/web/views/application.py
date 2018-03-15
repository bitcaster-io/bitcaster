# -*- coding: utf-8 -*-
"""
bitcaster / application
~~~~~~~~~~~~~~~~~

:copyright: (c) 2018 Stefano Apostolico, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

import logging

from django.contrib import messages
from django.core.cache import cache
from django.db.models import Q
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext as _
from django.views.generic import DetailView
from rest_framework.exceptions import PermissionDenied

from bitcaster.models import Application, Channel
from bitcaster.security import is_owner
from bitcaster.utils.dashboard import get_status, check_channels, check_events
from bitcaster.web.forms import ApplicationCreateForm
from bitcaster.web.views.base import (BitcasterBaseCreateView,
                                      SelectedApplicationMixin, BitcasterBaseDetailView)

from .channel import (ChannelCreateWizard, ChannelDeleteView,
                      ChannelDeprecateView, ChannelListView,
                      ChannelToggleView, ChannelUpdateView, )

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
    def get_queryset(self):
        return self.selected_application.channels.all()
        # TODO(sax) display system channels too.
        # need to review the template to hide editing/remove... links
        # return Channel.objects.filter(Q(system=True, enabled=True) |
        #                               Q(organization=self.selected_organization, application=None) |
        #                               Q(application=self.selected_application)
        #                               )

    def get_success_url(self):
        return reverse_lazy("app-channel-list",
                            args=[self.selected_organization.slug,
                                  self.selected_application.slug])


class ApplicationChannels(ApplicationViewMixin,
                          ChannelViewMixin, ChannelListView):
    template_name = 'bitcaster/application_channels.html'

    def get_context_data(self, **kwargs):
        kwargs['title'] = _("Application Channels")
        kwargs['create_url'] = reverse("app-channel-create",
                                       args=[self.selected_organization.slug,
                                             self.selected_application.slug,
                                             ])
        return super().get_context_data(**kwargs)


class ApplicationChannelUpdate(ApplicationViewMixin, ChannelViewMixin,
                               ChannelUpdateView):
    template_name = 'bitcaster/app_channel_configure.html'

    def get_extra_instance_kwargs(self):
        return {'organization': self.selected_organization,
                'application': self.selected_application}


class ApplicationChannelRemove(ApplicationViewMixin, ChannelDeleteView):
    template_name = 'bitcaster/app_channel_remove.html'


class ApplicationChannelToggle(ApplicationViewMixin, ChannelViewMixin,
                               ChannelToggleView):
    pattern_name = 'app-channel-list'


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
