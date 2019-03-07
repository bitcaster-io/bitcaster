from bitcaster.models import Subscription
from bitcaster.web.forms.user import UserSubscriptionForm
from bitcaster.web.views.base import (BitcasterBaseDeleteView,
                                      BitcasterBaseListView,
                                      BitcasterBaseToggleView,
                                      BitcasterBaseUpdateView,)
from bitcaster.web.views.organization.mixins import ApplicationListMixin

from ..mixins import SidebarMixin


class UserSubscriptionMixin:
    model = Subscription

    def get_queryset(self):
        return self.request.user.subscriptions.all()


class UserSubscriptionListView(ApplicationListMixin, SidebarMixin, UserSubscriptionMixin, BitcasterBaseListView):
    template_name = 'bitcaster/users/subscriptions.html'
    form_class = UserSubscriptionForm


class UserSubscriptionToggle(UserSubscriptionMixin, BitcasterBaseToggleView):
    def get_object(self, queryset=None):
        return self.get_queryset().get(id=self.kwargs['pk'])


class UserSubscriptionRemove(UserSubscriptionMixin, BitcasterBaseDeleteView):

    def get_object(self, queryset=None):
        return self.get_queryset().get(id=self.kwargs['pk'])


class UserSubscriptionEdit(UserSubscriptionMixin, SidebarMixin, BitcasterBaseUpdateView):
    def get_object(self, queryset=None):
        return self.get_queryset().get(id=self.kwargs['pk'])
