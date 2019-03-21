from django.urls import reverse
from django.utils.translation import gettext as _

from bitcaster.models import Subscription
from bitcaster.web.views.base import (BitcasterBaseDeleteView,
                                      BitcasterBaseListView,
                                      BitcasterBaseToggleView,
                                      BitcasterBaseUpdateView,)
from bitcaster.web.views.organization.mixins import ApplicationListMixin

from ..mixins import SidebarMixin


class UserSubscriptionMixin:
    model = Subscription
    title = _('Subscriptions')

    def get_queryset(self):
        return self.request.user.subscriptions.all()


class UserSubscriptionListView(ApplicationListMixin, SidebarMixin, UserSubscriptionMixin, BitcasterBaseListView):
    template_name = 'bitcaster/user/subscriptions.html'


class UserSubscriptionToggle(ApplicationListMixin, UserSubscriptionMixin, BitcasterBaseToggleView):
    def get_object(self, queryset=None):
        return self.get_queryset().get(id=self.kwargs['pk'])


class UserSubscriptionRemove(ApplicationListMixin, UserSubscriptionMixin, BitcasterBaseDeleteView):

    def get_success_url(self):
        return reverse('user-subscriptions', args=[self.selected_organization.slug])

    def get_object(self, queryset=None):
        return self.get_queryset().get(id=self.kwargs['pk'])


class UserSubscriptionEdit(UserSubscriptionMixin, SidebarMixin, BitcasterBaseUpdateView):
    def get_object(self, queryset=None):
        return self.get_queryset().get(id=self.kwargs['pk'])
