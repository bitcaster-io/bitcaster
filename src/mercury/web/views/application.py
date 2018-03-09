# -*- coding: utf-8 -*-
"""
mercury / application
~~~~~~~~~~~~~~~~~

:copyright: (c) 2018 Stefano Apostolico, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

import logging

from django.contrib import messages
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext as _
from django.views.generic import DetailView
from rest_framework.exceptions import PermissionDenied

from mercury.models import Application
from mercury.security import is_owner
from mercury.web.forms import ApplicationCreateForm
from mercury.web.views.base import (MercuryBaseCreateView,
                                    SelectedApplicationMixin,)

from .channel import (ChannelCreateWizard, ChannelDeleteView,
                      ChannelDeprecateView, ChannelListView,
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
           ]


class ApplicationViewMixin(SelectedApplicationMixin):
    model = Application
    slug_url_kwarg = 'app'

    def dispatch(self, request, *args, **kwargs):
        if not is_owner(request.user, self.selected_application):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class ApplicationCreate(MercuryBaseCreateView):
    model = Application
    form_class = ApplicationCreateForm

    def get_success_url(self):
        return reverse('app-index', args=[self.selected_organization.slug,
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

    def get_success_url(self):
        return reverse_lazy("org-channels",
                            args=[self.selected_organization.slug,
                                  self.selected_application.slug])


class ApplicationChannels(ApplicationViewMixin,
                          ChannelViewMixin, ChannelListView):
    template_name = 'mercury/application_channels.html'

    def get_context_data(self, **kwargs):
        kwargs['title'] = _("Application Channels")
        kwargs['create_url'] = reverse("org-channel-create",
                                       args=[self.selected_application.slug])
        return super().get_context_data(**kwargs)


class ApplicationChannelUpdate(ApplicationViewMixin, ChannelViewMixin,
                               ChannelUpdateView):
    template_name = 'bitcaster/org_channel_configure.html'


class ApplicationChannelRemove(ApplicationViewMixin, ChannelDeleteView):
    template_name = 'bitcaster/org_channel_remove.html'


class ApplicationChannelToggle(ApplicationViewMixin, ChannelViewMixin,
                               ChannelToggleView):
    pattern_name = 'org-channels'


class ApplicationChannelDeprecate(ApplicationViewMixin, ChannelViewMixin, ChannelDeprecateView):
    pattern_name = 'org-channels'


class ApplicationChannelCreate(ApplicationViewMixin, ChannelCreateWizard):
    TEMPLATES = {"a": "bitcaster/org_channel_wizard1.html",
                 "b": "bitcaster/org_channel_wizard2.html",
                 }
