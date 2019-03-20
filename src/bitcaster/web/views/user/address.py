# -*- coding: utf-8 -*-
import logging

from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from bitcaster.models import Address, AddressAssignment
from bitcaster.web.forms import (AddressAssignmentForm,
                                 AddressAssignmentFormSet, AddressForm,
                                 AddressFormSet,)

from ..base import BitcasterBaseDetailView, BitcasterBaseUpdateView
from .base import UserMixin

logger = logging.getLogger(__name__)

__all__ = ('UserAddressesView', 'UserAddressesInfoView', 'UserAddressesAssignmentView')


class UserAddressesView(UserMixin, BitcasterBaseUpdateView):
    template_name = 'bitcaster/user/addresses.html'
    model = Address
    form_class = AddressForm
    title = _('Addresses')

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse('user-address', args=[self.selected_organization.slug])

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


class UserAddressesInfoView(UserMixin, BitcasterBaseDetailView):
    template_name = 'bitcaster/user/address_usage.html'
    model = AddressAssignment

    def get_context_data(self, **kwargs):
        kwargs['handler'] = self.object.channel.handler
        kwargs['usage'] = self.object.channel.handler.get_usage()
        return super().get_context_data(**kwargs)


class UserAddressesAssignmentView(UserMixin, BitcasterBaseUpdateView):
    template_name = 'bitcaster/user/addresses_assignment.html'
    model = AddressAssignment
    form_class = AddressAssignmentForm
    title = _('Address Usage')

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse('user-address-assignment', args=[self.selected_organization.slug])

    def get_form_class(self):
        return AddressAssignmentFormSet

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.request.user
        return kwargs

    def form_invalid(self, form):
        self.error_user('Please correct errors below')
        return super().form_invalid(form)

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
        return super().form_valid(formset)
