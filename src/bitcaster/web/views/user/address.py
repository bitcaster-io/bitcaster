import logging
import string

from django.core.cache import caches
from django.db.models import Count, Q
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from bitcaster.models import Address, AddressAssignment
from bitcaster.models.audit import AuditLogEntry
from bitcaster.utils.strings import random_string
from bitcaster.web.forms.address import UserAddressForm

from ..base import (BitcasterBaseCreateView, BitcasterBaseDeleteView,
                    BitcasterBaseDetailView, BitcasterBaseListView,
                    BitcasterBaseUpdateView, BitcasterTemplateView,)
from .base import LogAuditMixin, UserMixin

logger = logging.getLogger(__name__)

__all__ = ('UserAddressesView', 'UserAddressesInfoView', 'UserAddressesAssignmentView')

cache = caches['default']


class UserAddressCreate(UserMixin, LogAuditMixin, BitcasterBaseCreateView):
    template_name = 'bitcaster/user/address/form.html'
    model = Address
    form_class = UserAddressForm

    def get_queryset(self):
        return self.request.user.addresses.all()

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['organization'] = self.selected_organization
        return kwargs

    def get_success_url(self):
        return reverse('user-address', args=[self.selected_organization.slug])

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        self.object = Address.objects.create(user=self.request.user,
                                             address=form.cleaned_data['address'],
                                             label=form.cleaned_data['label'])
        for c in form.cleaned_data['channels']:
            AddressAssignment.objects.create(
                user=self.request.user,
                channel=c,
                address=self.object,
                verified=False,
                code=random_string(8, string.digits)
            )
        return HttpResponseRedirect(self.get_success_url())


class UserAddressUpdate(UserMixin, LogAuditMixin, BitcasterBaseUpdateView):
    template_name = 'bitcaster/user/address/form.html'
    model = Address
    form_class = UserAddressForm

    def get_queryset(self):
        return self.request.user.addresses.unlocked()

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['organization'] = self.selected_organization
        return kwargs

    def get_success_url(self):
        return reverse('user-address', args=[self.selected_organization.slug])

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        self._old_value = obj.address
        return obj

    def form_valid(self, form):

        invalidate = False
        self.object.user = self.request.user
        if self.object.address != self._old_value:
            invalidate = True

        # self.object.label = form.cleaned_data['label']
        self.object.save()
        qs = AddressAssignment.objects.unlocked(user=self.request.user,
                                                address=self.object)
        # delete removed channels
        qs.exclude(channel__in=form.cleaned_data['channels']).delete()

        selected_channels = list(form.cleaned_data['channels'])

        existing_channels = [e.channel for e in
                             qs.filter(channel__in=selected_channels)]
        new_channels = [item for item in selected_channels if item not in existing_channels]

        for ch in new_channels:
            AddressAssignment.objects.create(
                user=self.request.user,
                channel=ch,
                address=self.object,
                verified=False,
                code=random_string(8, string.digits)
            )

        if invalidate:
            for ch in existing_channels:
                qs.filter(channel=ch, address=self.object).update(
                    verified=False,
                    code=random_string(8, string.digits)
                )

        return HttpResponseRedirect(self.get_success_url())


class UserAddressDelete(UserMixin, LogAuditMixin, BitcasterBaseDeleteView):
    model = Address

    def get_queryset(self):
        return self.request.user.addresses.unlocked()

    def get_success_url(self):
        return reverse('user-address', args=[self.selected_organization.slug])


class UserAddressesView(UserMixin, LogAuditMixin, BitcasterBaseListView):
    template_name = 'bitcaster/user/address/list.html'
    model = Address
    # form_class = AddressForm
    title = _('Addresses')

    def get_queryset(self):
        qs = self.request.user.addresses.unlocked()
        return qs.annotate(c=Count('assignments',
                                   filter=Q(assignments__user=self.request.user)
                                   ))

    def get_context_data(self, **kwargs):
        return super().get_context_data(locked_addresses=self.request.user.addresses.locked().order_by('label'),
                                        cache_version=2,
                                        **kwargs)

    def get_success_url(self):
        return reverse('user-address', args=[self.selected_organization.slug])


class UserAddressesVerifyView(UserMixin, LogAuditMixin, BitcasterTemplateView):
    template_name = 'bitcaster/user/address/verify.html'
    model = AddressAssignment
    mode = ''  # verify or resend

    def get_object(self, queryset=None):
        return self.request.user.assignments.get(pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        self.object = self.get_object()
        kwargs['handler'] = self.object.channel.handler
        kwargs['usage'] = self.object.channel.handler.get_usage()
        return super().get_context_data(object=self.object, **kwargs)

    def get(self, request, *args, **kwargs):
        if self.mode == 'form':
            context = self.get_context_data(channel_enabled=self.get_object().channel.enabled, **kwargs)
            return self.render_to_response(context)
        else:  # self.mode == 'resend'
            assignment = self.get_object()
            try:
                recipient = assignment.send_verification_code()
                return JsonResponse({'status': 'sent',
                                     'recipient': recipient})
            except Exception as e:
                msg = 'Error sendig code to %s: %s' % (assignment.address.address, str(e))
                return JsonResponse({'status': 'error',
                                     'message': msg}, status=400)

    def post(self, request, *args, **kwargs):
        code = request.POST.get('code')
        assignment = self.get_object()
        if assignment.code_is_valid(code):
            self.audit(assignment.address,
                       AuditLogEntry.AuditEvent.ADDRESS_VERIFIED)
            return JsonResponse({'status': 'success',
                                 'message': 'Address Verified'})

            # url = reverse('user-address-assignment', args=[self.selected_organization.slug])
            # return HttpResponseRedirect(url)
        else:
            return JsonResponse({'status': 'error',
                                 'message': 'Invalid Code'}, status=400)
        #
    # def get_object(self, queryset=None):
    #     return self.request.user.assignments.get(pk=self.kwargs[self.pk_url_kwarg])


class UserAddressesInfoView(UserMixin, BitcasterBaseDetailView):
    template_name = 'bitcaster/user/address_usage.html'
    model = AddressAssignment

    def get_context_data(self, **kwargs):
        kwargs['handler'] = self.object.channel.handler
        kwargs['usage'] = self.object.channel.handler.get_usage()
        return super().get_context_data(**kwargs)


class UserAddressesAssignmentView(UserMixin, LogAuditMixin, BitcasterTemplateView):
    template_name = 'bitcaster/user/address/assignment.html'
    title = _('addresses verification')

    # model = AddressAssignment
    # form_class = AddressAssignmentFormSet
    # title = _('Address Usage')

    def get_object(self, queryset=None):
        return self.request.user

    # def get_success_url(self):
    #     return reverse('user-address-assignment', args=[self.selected_organization.slug])
    #
    # def post(self, request, *args, **kwargs):
    #     return super().post(request, *args, **kwargs)
    #
    # def get_form_kwargs(self):
    #     kwargs = super().get_form_kwargs()
    #     kwargs['instance'] = self.request.user
    #     kwargs['organization'] = self.selected_organization
    #     return kwargs
    #
    # def form_invalid(self, form):
    #     self.error_user('Please correct errors below')
    #     return super().form_invalid(form)
    #
    # def form_valid(self, formset):
    #     formset.instance = self.request.user
    #     formset.save()
    #
    #     for a in formset.deleted_objects:
    #         self.audit(a, AuditLogEntry.AuditEvent.ASSIGNMENT_DELETED)
    #     if formset.new_objects:
    #         self.message_user(_('To complete your configuration. Insert codes that you receive to each new address'))
    #         for assignment in formset.new_objects:
    #             self.audit(assignment, AuditLogEntry.AuditEvent.ASSIGNMENT_CREATED)
    #
    #     for assignment, changed_data in formset.changed_objects:
    #         self.audit(assignment, AuditLogEntry.AuditEvent.ASSIGNMENT_UPDATED,
    #                    data=changed_data)
    #         disabled = self.request.user.subscriptions.filter(channel=assignment.channel,
    #                                                           enabled=True).update(
    #             enabled=assignment.address.verified)
    #         if disabled:
    #             message = ngettext_lazy(
    #                 '%s subscription has been disabled.' % disabled,
    #                 '%s subscriptions have been disabled.' % disabled,
    #                 disabled)
    #             self.message_user(message)
    #     return super().form_valid(formset)
