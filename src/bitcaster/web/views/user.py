# -*- coding: utf-8 -*-
import logging

from django.contrib import messages
from django.utils.functional import cached_property
from django.utils.translation import gettext as _

from bitcaster.models import User, Organization
from bitcaster.utils.wsgi import get_client_ip

from ..forms import UserProfileForm
from .base import BitcasterBaseUpdateView, BitcasterTemplateView, BitcasterBaseDetailView

logger = logging.getLogger(__name__)

__all__ = ["UserProfileView", "UserWelcomeView", "UserHomeView"]


class UserHomeView(BitcasterBaseDetailView):
    template_name = "bitcaster/users/user-home.html"
    model = User

    @cached_property
    def selected_organization(self):
        return Organization.objects.get(slug=self.kwargs['org'],
                                        members=self.request.user,
                                        )

    @cached_property
    def selected_application(self):
        return self.selected_organization.applications.get(slug=self.kwargs['app'])

    def get_context_data(self, **kwargs):
        kwargs['application'] = self.selected_application
        allowed_applications = []
        for m in self.request.user.memberships.all():
            for application in m.organization.applications.all():
                allowed_applications.append(
                (m.organization, application)
            )
        return super().get_context_data(**kwargs)

    def get_object(self, queryset=None):
        return self.request.user


class UserWelcomeView(BitcasterTemplateView):
    template_name = "bitcaster/users/user-welcome.html"


class UserProfileView(BitcasterBaseUpdateView):
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
