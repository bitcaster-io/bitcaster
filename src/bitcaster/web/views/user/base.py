# -*- coding: utf-8 -*-
import logging

from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView

from bitcaster import messages
from bitcaster.models import Address, AddressAssignment, User
from bitcaster.utils.email_verification import set_new_email_request
from bitcaster.web.forms import (AddressAssignmentForm,
                                 AddressAssignmentFormSet, AddressForm,
                                 AddressFormSet, UserProfileForm,
                                 send_address_verification_email,)
from bitcaster.web.views.organization.mixins import SelectedOrganizationMixin

from ..base import BitcasterBaseDetailView, BitcasterBaseUpdateView
from ..mixins import SidebarMixin, TitleMixin

logger = logging.getLogger(__name__)

__all__ = ('UserProfileView', 'UserAddressesView',
           'UserAddressesInfoView', 'UserAddressesAssignmentView')


class UserMixin(SelectedOrganizationMixin, SidebarMixin, TitleMixin):
    pass


class UserHome(UserMixin, TemplateView):
    template_name = 'bitcaster/user/home.html'
    title = _('Home')


class UserEventListView(UserMixin, TemplateView):
    template_name = 'bitcaster/user/events.html'
    title = _('Events')


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
    template_name = 'bitcaster/user/address_info.html'
    model = Address


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


class UserProfileView(UserMixin, BitcasterBaseUpdateView):
    template_name = 'bitcaster/user/profile.html'
    model = User
    form_class = UserProfileForm
    success_url = '.'
    title = _('My Profile')

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        ret = super().get_context_data(**kwargs)

        if ret['form'].new_email_pending:
            ret['newemail'] = ret['form'].new_email_pending
        return ret

    def form_valid(self, form):
        email_changed = form.fields['email'].has_changed(form.initial.get('email'),
                                                         form.data.get('email'))

        if email_changed:
            set_new_email_request(form.instance, form.data['email'])
            send_address_verification_email(form.instance)
            form.instance.email = form.initial['email']
            self.message_user(_('Check your inbox to validate your new email address'), messages.SUCCESS)
        ret = super().form_valid(form)
        # self.message_user(_('Profile Updated'), messages.SUCCESS)
        return ret
