from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import ListView, TemplateView

from mercury.db.fields import Role
from mercury.models import Event, Message, Subscription

from .base import SelectedApplicationMixin

__all__ = ("EventList", "IndexView",
           "MessageList", "SubscriptionList", "WorkInProgressView")


class SubscriptionList(SelectedApplicationMixin, ListView):
    model = Subscription

    def get_queryset(self):
        return Subscription.objects.filter(event__application=self.selected_application)


class EventList(SelectedApplicationMixin, ListView):
    model = Event

    def get_queryset(self):
        return self.selected_application.events.all()


class MessageList(SelectedApplicationMixin, ListView):
    model = Message

    def get_queryset(self):
        return self.selected_application.messages.all()


class WorkInProgressView(TemplateView):
    template_name = 'bitcaster/wip.html'


class IndexView(TemplateView):
    template_name = 'bitcaster/index.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.memberships.filter(role=Role.OWNER):
                url = reverse('org-index', args=[request.user.memberships.first().organization.slug])
                return HttpResponseRedirect(url)
        return super().get(request, *args, **kwargs)
