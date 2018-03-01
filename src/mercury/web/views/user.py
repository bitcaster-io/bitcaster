# -*- coding: utf-8 -*-
"""
mercury / user
~~~~~~~~~~~~~~~~~

:copyright: (c) 2018 Stefano Apostolico, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

import logging

from django.urls import reverse_lazy
from django.utils.translation import gettext as _
from django.views.generic import UpdateView

from mercury.models import User
from mercury.web.forms import UserProfileForm

logger = logging.getLogger(__name__)


class UserProfile(UpdateView):
    template_name = 'bitcaster/users/profile.html'
    model = User
    form_class = UserProfileForm
    success_url = reverse_lazy('home')

    def get_object(self, queryset=None):
        return self.request.user

    # def get_form_class(self):
    #     fields = UserCreationForm._meta.fields
    #     return modelform_factory(User, fields=fields)
