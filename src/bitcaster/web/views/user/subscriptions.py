from django.urls import reverse
from django.utils.translation import gettext as _

from bitcaster import messages
from bitcaster.middleware.exception import RedirectToRefererResponse
from bitcaster.models import Subscription
from bitcaster.web.views.base import (BitcasterBaseDeleteView,
                                      BitcasterBaseListView,
                                      BitcasterBaseToggleView,
                                      BitcasterBaseUpdateView,)

from .base import UserMixin


class UserSubscriptionMixin(UserMixin):
    model = Subscription
    title = _('Subscriptions')

    def get_queryset(self):
        return self.request.user.subscriptions.all()


class UserSubscriptionListView(UserSubscriptionMixin, BitcasterBaseListView):
    template_name = 'bitcaster/user/subscriptions.html'


class UserSubscriptionToggle(UserSubscriptionMixin, BitcasterBaseToggleView):
    def get_object(self, queryset=None):
        return self.get_queryset().get(id=self.kwargs['pk'])

    def get(self, request, *args, **kwargs):
        obj = self.get_object()
        try:
            if obj.recipient:
                obj.enabled = not obj.enabled
                if obj.enabled:
                    self.message_user(f'{obj._meta.verbose_name} #{obj.pk} enabled',
                                  level=messages.SUCCESS)
                else:
                    self.message_user(f'{obj._meta.verbose_name} #{obj.pk} disabled',
                                  level=messages.WARNING)
        except Exception:
            obj.enabled = False
            self.message_user(_('{} #{} cannot be enabled because '
                                'there are no valid address').format(obj._meta.verbose_name, obj.pk),
                              level=messages.WARNING)

        obj.save()
        return RedirectToRefererResponse(request)


class UserSubscriptionRemove(UserSubscriptionMixin, BitcasterBaseDeleteView):

    def get_success_url(self):
        return reverse('user-subscriptions', args=[self.selected_organization.slug])

    def get_object(self, queryset=None):
        return self.get_queryset().get(id=self.kwargs['pk'])


class UserSubscriptionEdit(UserSubscriptionMixin, BitcasterBaseUpdateView):
    def get_object(self, queryset=None):
        return self.get_queryset().get(id=self.kwargs['pk'])
