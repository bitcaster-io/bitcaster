from django.views.generic import DetailView, ListView

from mercury.models import (Application, Channel, Event,
                            Message, Organization, Subscription,)
from mercury.web.views.base import (ApplicationListMixin,
                                    SelectedApplicationMixin,
                                    SelectedOrganizationMixin,)


# @method_decorator(login_required, name='dispatch')
class OrganizationDetail(SelectedOrganizationMixin, ApplicationListMixin, DetailView):
    model = Organization
    slug_url_kwarg = 'org'


# @method_decorator(login_required, name='dispatch')
class ApplicationDetail(SelectedApplicationMixin, DetailView):
    model = Application
    slug_url_kwarg = 'app'


# @method_decorator(login_required, name='dispatch')
class SubscriptionList(SelectedApplicationMixin, ListView):
    model = Subscription

    def get_queryset(self):
        return Subscription.objects.filter(event__application=self.selected_application)


class EventList(SelectedApplicationMixin, ListView):
    model = Event

    def get_queryset(self):
        return self.selected_application.events.all()


class ChannelList(SelectedApplicationMixin, ListView):
    model = Channel

    def get_queryset(self):
        return self.selected_application.channels.all()


class MessageList(SelectedApplicationMixin, ListView):
    model = Message

    def get_queryset(self):
        return self.selected_application.messages.all()
