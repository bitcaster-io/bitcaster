from django.contrib import messages
from django.views.generic import DetailView, ListView, CreateView
from django.utils.translation import gettext as _
from mercury.models import (Application, Channel, Event,
                            Message, Organization, Subscription, )
from mercury.web.forms import OrganizationForm, ApplicationForm, ApplicationCreateForm
from mercury.web.views.base import (ApplicationListMixin,
                                    SelectedApplicationMixin,
                                    SelectedOrganizationMixin, MercuryBaseCreateView, MercuryBaseDetailView)


# @method_decorator(login_required, name='dispatch')
class OrganizationDetail(MercuryBaseDetailView):
    model = Organization
    slug_url_kwarg = 'org'


class OrganizationCreate(MercuryBaseCreateView):
    model = Organization
    form_class = OrganizationForm
    success_url = '.'

    def form_valid(self, form):
        # form.cleaned_data['owner'] = self.request.user
        form.instance.owner = self.request.user
        self.message_user(_('Organization created'), messages.SUCCESS)
        return super().form_valid(form)


class ApplicationCreate(MercuryBaseCreateView):
    model = Application
    form_class = ApplicationCreateForm
    success_url = '.'

    def form_valid(self, form):
        # form.cleaned_data['owner'] = self.request.user
        form.instance.organization = self.selected_organization
        self.message_user(_('Application created'), messages.SUCCESS)
        return super().form_valid(form)


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
