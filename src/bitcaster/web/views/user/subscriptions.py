import logging

from django.urls import reverse
from django.utils.translation import gettext as _

from bitcaster import messages
from bitcaster.exceptions import AddressNotVerified
from bitcaster.models import Address, AuditEvent, AuditLogEntry, Subscription
from bitcaster.web.forms.user import UserSubscriptionEditForm
from bitcaster.web.views.base import (BitcasterBaseDeleteView,
                                      BitcasterBaseListView,
                                      BitcasterBaseToggleView,
                                      BitcasterBaseUpdateView,
                                      HttpResponseRedirectToReferrer,)

from .base import LogAuditMixin, UserMixin

logger = logging.getLogger()


class UserSubscriptionMixin(UserMixin):
    model = Subscription
    title = _('Subscriptions')

    def get_queryset(self):
        return self.request.user.subscriptions.all()


class UserSubscriptionListView(UserSubscriptionMixin, BitcasterBaseListView):
    template_name = 'bitcaster/user/subscriptions/list.html'

    def get_queryset(self):
        return super().get_queryset().order_by('event__application__name', 'event__name', 'id')


class UserSubscriptionToggle(UserSubscriptionMixin, LogAuditMixin, BitcasterBaseToggleView):
    def get_object(self, queryset=None):
        return self.get_queryset().get(id=self.kwargs['pk'])

    def get(self, request, *args, **kwargs):
        subscription = self.get_object()
        try:
            assignment = request.user.assignments.get(channel=subscription.channel)
            if assignment and not assignment.address.verified:
                raise AddressNotVerified()

            subscription.enabled = not subscription.enabled
            if subscription.enabled:
                self.message_user(f'{subscription._meta.verbose_name} #{subscription.pk} enabled',
                                  level=messages.SUCCESS)
            else:
                self.message_user(f'{subscription._meta.verbose_name} #{subscription.pk} disabled',
                                  level=messages.WARNING)
        except AddressNotVerified:
            subscription.enabled = False
            self.message_user(_('{} #{} cannot be enabled because '
                                'address has not been verified').format(subscription._meta.verbose_name,
                                                                        subscription.pk),
                              level=messages.WARNING)

        except Address.DoesNotExist as e:
            logger.exception(e)
            subscription.enabled = False
            self.message_user(_('{} #{} cannot be enabled because '
                                'there is no valid address to use').format(
                subscription._meta.verbose_name, subscription.pk, e),
                level=messages.WARNING)
        if subscription.enabled:
            event = AuditEvent.SUBSCRIPTION_ENABLED
        else:
            event = AuditEvent.SUBSCRIPTION_DISABLED
        self.audit(subscription, event)

        subscription.save()

        return HttpResponseRedirectToReferrer(request)


class UserSubscriptionRemove(UserSubscriptionMixin, LogAuditMixin, BitcasterBaseDeleteView):

    def get_success_url(self):
        return reverse('user-subscriptions', args=[self.selected_organization.slug])

    def get_object(self, queryset=None):
        return self.get_queryset().get(id=self.kwargs['pk'])

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        self.audit(obj, AuditLogEntry.AuditEvent.SUBSCRIPTION_DELETED)

        return super().delete(request, *args, **kwargs)


class UserSubscriptionEdit(UserSubscriptionMixin, BitcasterBaseUpdateView):
    template_name = 'bitcaster/user/subscriptions/form.html'
    form_class = UserSubscriptionEditForm
    title = _('Change Subscription Channel')

    def get_success_url(self):
        return reverse('user-subscriptions', args=[self.selected_organization.slug])

    def get_object(self, queryset=None):
        return self.get_queryset().get(id=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        self.object = self.get_object()
        # org  =
        ret = super().get_context_data(object=self.object, **kwargs)
        ret['not_usable_channels'] = self.object.event.channels.exclude(addresses__user=self.request.user,
                                                                        addresses__address__verified=True)
        ret['usable_channels'] = self.object.event.channels.filter(addresses__user=self.request.user,
                                                                   addresses__address__verified=True)
        return ret
