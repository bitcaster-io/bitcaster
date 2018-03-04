# -*- coding: utf-8 -*-
"""
mercury / application
~~~~~~~~~~~~~~~~~

:copyright: (c) 2018 Stefano Apostolico, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

import logging

from django.contrib import messages
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views.generic import DetailView

from mercury.models import Application
from mercury.web.forms import ApplicationCreateForm
from mercury.web.views.base import (MercuryBaseCreateView,
                                    SelectedApplicationMixin,)

logger = logging.getLogger(__name__)

__all__ = ["ApplicationCreate", "ApplicationDetail"]


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


class ApplicationDetail(SelectedApplicationMixin, DetailView):
    model = Application
    slug_url_kwarg = 'app'
