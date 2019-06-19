import logging

from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import gettext as _

from bitcaster.exceptions import AddressNotAssigned, AddressNotVerified
from bitcaster.models import (Address, AuditEvent, AuditLogEntry,
                              Event, Subscription,)
from bitcaster.web import messages
from bitcaster.web.forms.user import (UserSubscriptionCreateForm,
                                      UserSubscriptionEditForm,)
from bitcaster.web.views.base import (BitcasterBaseCreateView,
                                      BitcasterBaseDeleteView,
                                      BitcasterBaseListView,
                                      BitcasterBaseToggleView,
                                      BitcasterBaseUpdateView,
                                      HttpResponseRedirectToReferrer,)
from bitcaster.web.views.organization.mixins import SelectedOrganizationMixin

from .base import LogAuditMixin, UserMixin

logger = logging.getLogger()


class UserSubscriptionMixin(UserMixin):
    model = Subscription
    title = _('Subscriptions')

    def get_queryset(self):
        qs = self.request.user.subscriptions.select_related('event__application',
                                                            'assignment',
                                                            'assignment__address',
                                                            'channel',
                                                            'event').all()
        return qs


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
            if not subscription.assignment:
                raise AddressNotAssigned()
            if not subscription.recipient:
                raise AddressNotVerified()

            subscription.enabled = not subscription.enabled
            if subscription.enabled:
                self.message_user(f'{subscription._meta.verbose_name} #{subscription.pk} enabled',
                                  level=messages.SUCCESS)
            else:
                self.message_user(f'{subscription._meta.verbose_name} #{subscription.pk} disabled',
                                  level=messages.WARNING)
        except (AddressNotVerified, AddressNotAssigned) as e:
            subscription.enabled = False
            self.message_user(_('{} #{} cannot be enabled. {}').format(subscription._meta.verbose_name,
                                                                       subscription.pk,
                                                                       str(e)),
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


class UserSubscriptionCreate(SelectedOrganizationMixin, LogAuditMixin, BitcasterBaseCreateView):
    template_name = 'bitcaster/user/subscribe.html'
    title = 'Create subscriptions for %(object)s'
    form_class = UserSubscriptionCreateForm
    model = Subscription

    def get_success_url(self):
        return reverse('user-events', args=[self.selected_organization.slug])

    def get_object(self, queryset=None):
        self.object = Event.objects.get(id=self.kwargs['pk'])
        return self.object

    def get_context_data(self, **kwargs):
        self.event = self.get_object()
        ret = super().get_context_data(object=self.object, **kwargs)
        ret['existing_subscriptions'] = self.request.user.subscriptions.filter(event=self.event)
        ret['not_usable_channels'] = self.event.channels.exclude(assignments__user=self.request.user,
                                                                 assignments__verified=True)
        ret['usable_channels'] = self.event.channels.all()
        return ret

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['event'] = self.get_object()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        selection = form.cleaned_data['addresses']
        for a in self.request.user.assignments.filter(id__in=selection):
            obj, __ = Subscription.objects.get_or_create(subscriber=self.request.user,
                                                         assignment=a,
                                                         channel=a.channel,
                                                         event=form.event,
                                                         defaults={'trigger_by': self.request.user,
                                                                   'enabled': a.verified,
                                                                   'status': Subscription.STATUSES.OWNED})
            self.audit(obj, AuditLogEntry.AuditEvent.SUBSCRIPTION_CREATED)

        return HttpResponseRedirect(self.get_success_url())


class UserSubscriptionEdit(UserSubscriptionMixin, BitcasterBaseUpdateView):
    template_name = 'bitcaster/user/subscriptions/form.html'
    form_class = UserSubscriptionEditForm
    title = _('Change Subscriptions')

    def get_success_url(self):
        return reverse('user-subscriptions', args=[self.selected_organization.slug])

    def get_object(self, queryset=None):
        return self.get_queryset().get(id=self.kwargs['pk'])
