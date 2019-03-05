# -*- coding: utf-8 -*-
import logging

from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView

from bitcaster import messages
from bitcaster.models import Address, AddressAssignment, User
from bitcaster.system import system
from bitcaster.utils.email_verification import set_new_email_request
from bitcaster.web.forms.user import (AddressAssignmentForm,
                                      AddressAssignmentFormSet, AddressForm,
                                      AddressFormSet,
                                      send_address_verification_email,)
from bitcaster.web.views.organization.mixins import ApplicationListMixin

from ..forms import UserProfileForm
from .base import (BitcasterBaseDetailView,
                   BitcasterBaseUpdateView, MessageUserMixin,)

logger = logging.getLogger(__name__)

__all__ = ('UserProfileView', 'UserAddressesView',
           'UserAddressesInfoView', 'UserAddressesAssignmentView')


class UserIndexView(ApplicationListMixin, MessageUserMixin, TemplateView):
    template_name = 'bitcaster/users/user-home.html'

    def get(self, request, *args, **kwargs):
        configured = self.selected_organization.configured

        if not configured and request.user.has_perm('org:configure', self.selected_organization):
            self.alarm(_('Configuration of this organization is not complete. '
                         '<a href="%s">Configure</a>') % reverse('org-dashboard',
                                                                 args=[self.selected_organization.slug]))

        if not system.configured and request.user.is_superuser:
            self.alarm(_('System configuration is not complete. '
                         '<a href="%s">Configure</a>') % reverse('settings'))

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        subscriptions = {}
        menu = {}

        ret = super().get_context_data(**kwargs)
        applications = ret['applications']
        for subscription in self.request.user.subscriptions.all():
            subscriptions[f'{subscription.event_id}-{subscription.channel_id}'] = subscription

        for application in applications:
            menu[application] = {}
            for event in application.events.all():
                menu[application][event] = {}
                for channel in event.channels.all():
                    menu[application][event][channel] = subscriptions.get(f'{event.id}-{channel.id}')
                ret['menu'] = menu

        membership = self.request.user.memberships.first()
        if membership:
            ret['setup_url'] = reverse('org-dashboard', args=[membership.organization.slug])

        return ret


class UserAddressesView(BitcasterBaseUpdateView):
    template_name = 'bitcaster/users/addresses.html'
    model = Address
    form_class = AddressForm
    title = _('Addresses')

    def get_object(self, queryset=None):
        return self.request.user

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
        self.message_user('Addresses updated', messages.SUCCESS)
        return super().form_valid(formset)


class UserAddressesInfoView(BitcasterBaseDetailView):
    template_name = 'bitcaster/users/address_info.html'
    model = Address


class UserAddressesAssignmentView(BitcasterBaseUpdateView):
    template_name = 'bitcaster/users/addresses_assignment.html'
    model = AddressAssignment
    form_class = AddressAssignmentForm
    title = _('Address Usage')

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse('user-address-assignment')

    def get_form_class(self):
        return AddressAssignmentFormSet

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.request.user
        return kwargs

    def form_valid(self, formset):
        formset.instance = self.request.user
        formset.save()
        for assignment in formset.new_objects:
            usage_message = assignment.channel.get_usage_message()
            if usage_message:
                self.message_user(usage_message, extra_tags='keep')
        for assignment, __ in formset.changed_objects:
            usage_message = assignment.channel.get_usage_message()
            if usage_message:
                self.message_user(usage_message, extra_tags='keep')
        self.message_user('Assignments updated', messages.SUCCESS)
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

    # def get_initial(self):
    #     initial = super().get_initial()
    #     user = self.get_object()
    # if not user.language:
    #     initial['language'] = self.request.LANGUAGE_CODE
    #
    # if not user.country or user.timezone:
    #     remote_ip = get_client_ip(self.request)
    #     if remote_ip:
    #         from geolite2 import geolite2
    #         reader = geolite2.reader()
    #         match = reader.get(remote_ip)
    #         if match:
    #             if not user.country:
    #                 try:
    #                     initial['country'] = match['country']['iso_code']
    #                 except KeyError:
    #                     initial['country'] = None
    #
    #             if not user.timezone:
    #                 try:
    #                     initial['timezone'] = match['location']['time_zone']
    #                 except KeyError:
    #                     initial['timezone'] = None
    # return initial

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
