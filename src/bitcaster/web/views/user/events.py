from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import gettext as _

from bitcaster.models import Event, Subscription, User
from bitcaster.models.subscription import SubscriptionStatus
from bitcaster.web.forms.user import UserSubscriptionForm
from bitcaster.web.views.base import (BitcasterBaseCreateView,
                                      BitcasterBaseListView,)
from bitcaster.web.views.organization.mixins import ApplicationListMixin

from ..mixins import SidebarMixin


class UserEventMixin:
    model = User
    title = _('Events')

    def get_queryset(self):
        return Event.objects.all()


class UserEventListView(ApplicationListMixin, SidebarMixin, UserEventMixin, BitcasterBaseListView):
    template_name = 'bitcaster/user/events.html'


class UserEventSubcribe(ApplicationListMixin, UserEventMixin, BitcasterBaseCreateView):
    template_name = 'bitcaster/user/subscribe.html'

    form_class = UserSubscriptionForm

    def get_success_url(self):
        return reverse('user-events', args=[self.selected_organization.slug])

    def get_object(self, queryset=None):
        return self.get_queryset().get(id=self.kwargs['pk'])

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.get_object()
        return kwargs

    def form_valid(self, form):
        for channel in form.cleaned_data['channels']:
            Subscription.objects.create(subscriber=self.request.user,
                                        trigger_by=self.request.user,
                                        event=form.event,
                                        channel=channel,
                                        enabled=True,
                                        status=SubscriptionStatus.OWNED)
        return HttpResponseRedirect(self.get_success_url())
