# -*- coding: utf-8 -*-
import logging
import string

from django.http import HttpResponseRedirect, JsonResponse
from django.template.defaultfilters import pluralize
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from bitcaster import messages
from bitcaster.models import Address, AddressAssignment
from bitcaster.models.audit import AuditLogEntry
from bitcaster.utils.strings import random_string
from bitcaster.web.forms import (AddressAssignmentForm,
                                 AddressAssignmentFormSet, AddressFormSet,)

from ..base import (BitcasterBaseDetailView,
                    BitcasterBaseUpdateView, BitcasterTemplateView,)
from .base import LogAuditMixin, UserMixin

logger = logging.getLogger(__name__)

__all__ = ('UserAddressesView', 'UserAddressesInfoView', 'UserAddressesAssignmentView')


class UserAddressesView(UserMixin, LogAuditMixin, BitcasterBaseUpdateView):
    template_name = 'bitcaster/user/addresses.html'
    model = Address
    # form_class = AddressForm
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
        for a in formset.deleted_objects:
            self.audit(event=AuditLogEntry.Event.MEMBER_DELETE_ADDRESS,
                       target_object=a.pk,
                       target_label=str(a))

        for obj, changed_data in formset.changed_objects:
            self.audit(event=AuditLogEntry.Event.MEMBER_UPDATE_ADDRESS,
                       data=changed_data,
                       target_object=obj.pk,
                       target_label=str(obj))

        for a in formset.new_objects:
            self.audit(event=AuditLogEntry.Event.MEMBER_ADD_ADDRESS,
                       target_object=a.pk,
                       target_label=str(a))

        return super().form_valid(formset)


class UserAddressesVerifyView(UserMixin, LogAuditMixin, BitcasterTemplateView):
    template_name = 'bitcaster/user/address_verify.html'
    model = AddressAssignment
    mode = ''  # verify or resend

    def get_object(self, queryset=None):
        return self.request.user.assignments.get(pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        return super().get_context_data(object=self.get_object(),
                                        **kwargs)

    def get(self, request, *args, **kwargs):
        if self.mode == 'form':
            context = self.get_context_data(**kwargs)
            return self.render_to_response(context)
        elif self.mode == 'resend':
            assignment = self.get_object()
            address = assignment.address
            code = random_string(6, string.digits)
            address.code = code
            address.save()
            try:
                recipient = assignment.channel.handler.emit(address.address,
                                                            'Bitcaster confirmation code',
                                                            'Bitcaster confirmation code %s' % code)
                return JsonResponse({'status': 'sent',
                                     'recipient': recipient})
            except Exception as e:
                return JsonResponse({'status': 'error',
                                     'message': str(e)}, status=400)

    def post(self, request, *args, **kwargs):
        code = request.POST.get('code')
        if code:
            assignment = self.get_object()
            if str(assignment.address.code) == code:
                assignment.address.verified = True
                assignment.address.save()
                self.message_user('Address verified', messages.SUCCESS)
                self.audit(event=AuditLogEntry.Event.MEMBER_VALIDATE_ADDRESS,
                           target_object=assignment.address.pk,
                           target_label=str(assignment))
            else:
                self.message_user('Invalid Code', messages.ERROR)
        url = reverse('user-address-assignment', args=[self.selected_organization.slug])
        return HttpResponseRedirect(url)

    # def get_object(self, queryset=None):
    #     return self.request.user.assignments.get(pk=self.kwargs[self.pk_url_kwarg])


class UserAddressesInfoView(UserMixin, BitcasterBaseDetailView):
    template_name = 'bitcaster/user/address_usage.html'
    model = AddressAssignment

    def get_context_data(self, **kwargs):
        kwargs['handler'] = self.object.channel.handler
        kwargs['usage'] = self.object.channel.handler.get_usage()
        return super().get_context_data(**kwargs)


class UserAddressesAssignmentView(UserMixin, LogAuditMixin, BitcasterBaseUpdateView):
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
        if formset.disabled_subscriptions:
            msg = _('{} subscriptions {} been disabled.').format(formset.disabled_subscriptions,
                                                                 pluralize(formset.disabled_subscriptions,
                                                                           'has,have'))
            self.message_user(msg, extra_tags='keep')

        for a in formset.deleted_objects:
            self.audit(event=AuditLogEntry.Event.MEMBER_DELETE_ASSIGNMENT,
                       target_object=a.pk,
                       target_label=str(a))

        for assignment in formset.new_objects:
            # usage_message = assignment.channel.get_usage_message()
            self.audit(event=AuditLogEntry.Event.MEMBER_ADD_ASSIGNMENT,
                       target_object=assignment.pk,
                       target_label=str(assignment))
            # if usage_message:
            #     self.message_user(_('This subscription is not complete. Check extra info'), extra_tags='keep')

        for assignment, changed_data in formset.changed_objects:
            # usage_message = assignment.channel.get_usage_message()
            # if usage_message:
            #     self.message_user(usage_message, extra_tags='keep')
            self.audit(event=AuditLogEntry.Event.MEMBER_CHANGE_ASSIGNMENT,
                       data=changed_data,
                       target_object=assignment.pk,
                       target_label=str(assignment))

        return super().form_valid(formset)
