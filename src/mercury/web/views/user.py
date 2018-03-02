# -*- coding: utf-8 -*-
"""
mercury / user
~~~~~~~~~~~~~~~~~

:copyright: (c) 2018 Stefano Apostolico, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

import logging

from django.contrib import messages
from django.views.generic import UpdateView
from django.utils.translation import gettext as _
from mercury.models import User
from mercury.utils.wsgi import get_client_ip
from mercury.web.forms import UserProfileForm
from mercury.web.views.base import MessageUserMixin, MercuryBaseUpdateView

logger = logging.getLogger(__name__)


class UserProfileView(MercuryBaseUpdateView):
    template_name = 'bitcaster/users/profile.html'
    model = User
    form_class = UserProfileForm
    success_url = '.'

    def get_object(self, queryset=None):
        return self.request.user

    def get_initial(self):
        initial = super().get_initial()
        user = self.get_object()
        if not user.language:
            initial['language'] = self.request.LANGUAGE_CODE

        if not user.country or user.timezone:
            remote_ip = get_client_ip(self.request)
            if remote_ip:
                from geolite2 import geolite2
                reader = geolite2.reader()
                match = reader.get(remote_ip)
                if match:
                    if not user.country:
                        initial['country'] = match['country']['iso_code']
                    if not user.timezone:
                        initial['timezone'] = match['location']['time_zone']
        return initial


    def form_valid(self, form):
        ret = super().form_valid(form)
        self.message_user(_('Profile Updated'), messages.SUCCESS)
        return ret
    # def get_form_class(self):
    #     fields = UserCreationForm._meta.fields
    #     return modelform_factory(User, fields=fields)
