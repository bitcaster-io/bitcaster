# -*- coding: utf-8 -*-
import logging

from django import forms
from django.contrib import messages
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.translation import gettext as _
from django.views.generic import FormView

from bitcaster.models import Address, Organization, User
from bitcaster.utils.email_verification import set_new_email_request
from bitcaster.utils.wsgi import get_client_ip
from bitcaster.web.forms.user import send_address_verification_email

from ..forms import UserProfileForm
from .base import (BitcasterBaseDetailView,
                   BitcasterBaseUpdateView, BitcasterTemplateView,)

logger = logging.getLogger(__name__)

__all__ = ("UserProfileView", "UserWelcomeView", "UserHomeView", "UserAddressesView")


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


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ('id', 'user', 'dispatcher', 'address')


# class SubscriptionBaseFormSet(BaseInlineFormSet):
#
#     def __init__(self, *args, **kwargs):
#         self.event = kwargs.pop('event')
#         super().__init__(*args, **kwargs)
#         self.form_kwargs['event'] = self.event


AddressFormSet = forms.inlineformset_factory(User,
                                             Address,
                                             form=AddressForm,
                                             # formset=SubscriptionBaseFormSet,
                                             min_num=1,
                                             extra=0)


class UserAddressesView(FormView):
    template_name = 'bitcaster/users/addresses.html'
    model = Address
    form_class = AddressForm

    def get_success_url(self):
        return reverse('user-addresses')

    def get_form_class(self):
        return AddressFormSet

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.request.user
        return kwargs

    def form_valid(self, formset):
        formset.instance = self.request.user
        formset.save()
        return super().form_valid(formset)


class UserProfileView(BitcasterBaseUpdateView):
    template_name = 'bitcaster/users/profile.html'
    model = User
    form_class = UserProfileForm
    success_url = '.'

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        ret = super().get_context_data(**kwargs)

        if ret['form'].new_email_pending:
            ret['newemail'] = ret['form'].new_email_pending
        return ret

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
                        try:
                            initial['country'] = match['country']['iso_code']
                        except KeyError:
                            initial['country'] = None

                    if not user.timezone:
                        try:
                            initial['timezone'] = match['location']['time_zone']
                        except KeyError:
                            initial['timezone'] = None
        return initial

    def form_valid(self, form):
        email_changed = form.fields['email'].has_changed(form.initial.get('email'),
                                                         form.data.get('email'))

        if email_changed:
            set_new_email_request(form.instance, form.data['email'])
            send_address_verification_email(form.instance)
            form.instance.email = form.initial['email']
            self.message_user(_('Check your inbox to validate your new email address'), messages.SUCCESS)
        ret = super().form_valid(form)
        self.message_user(_('Profile Updated'), messages.SUCCESS)
        return ret
