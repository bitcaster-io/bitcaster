import logging

from django.urls import reverse
from django.utils.translation import gettext as _

from bitcaster import messages
from bitcaster.models import AuditEvent, AuditLogEntry, Subscription
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
        obj = self.get_object()
        try:
            assert obj.recipient  # address or assignment could be deleted
            obj.enabled = not obj.enabled
            if obj.enabled:
                self.message_user(f'{obj._meta.verbose_name} #{obj.pk} enabled',
                                  level=messages.SUCCESS)
            else:
                self.message_user(f'{obj._meta.verbose_name} #{obj.pk} disabled',
                                  level=messages.WARNING)
        except Exception as e:
            logger.exception(e)
            obj.enabled = False
            self.message_user(_('{} #{} cannot be enabled because '
                                'there are no valid address').format(obj._meta.verbose_name, obj.pk),
                              level=messages.WARNING)
        event = AuditEvent.MEMBER_ENABLE_SUBSCRIPTION if obj.enabled else AuditEvent.MEMBER_DISABLE_SUBSCRIPTION
        self.audit(event=event,
                   target_object=obj.pk,
                   target_label=str(obj),
                   data={'enabled': obj.enabled})

        obj.save()

        return HttpResponseRedirectToReferrer(request)


class UserSubscriptionRemove(UserSubscriptionMixin, LogAuditMixin, BitcasterBaseDeleteView):

    def get_success_url(self):
        return reverse('user-subscriptions', args=[self.selected_organization.slug])

    def get_object(self, queryset=None):
        return self.get_queryset().get(id=self.kwargs['pk'])

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        self.audit(event=AuditLogEntry.AuditEvent.MEMBER_DELETE_SUBSCRIPTION,
                   target_object=obj.pk,
                   target_label=str(obj))

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
