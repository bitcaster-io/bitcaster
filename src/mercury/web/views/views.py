from constance import config
from django.contrib import messages
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views.generic import DetailView, ListView
from django.views.generic.edit import FormView

from mercury.models import (Application, Channel, Event,
                            Message, Organization, Subscription,)
from mercury.web.forms import (ApplicationCreateForm, OrganizationForm,
                               SettingsChannelsForm, SettingsEmailForm,
                               SettingsMainForm, SettingsOAuthForm,)
from mercury.web.views.base import (MercuryBaseCreateView,
                                    MercuryBaseDetailView, MercuryTemplateView,
                                    SelectedApplicationMixin,
                                    SuperuserViewMixin,)


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

    def get_success_url(self):
        return reverse('app-index', args=[self.selected_organization.slug,
                                          self.object.slug])

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


class SettingsView(SuperuserViewMixin, MercuryTemplateView, FormView):
    success_url = '.'
    form_map = {'email': SettingsEmailForm,
                'main': SettingsMainForm,
                'channels': SettingsChannelsForm,
                'oauth': SettingsOAuthForm,
                }
    title_map = {'email': "Email",
                 "main": "General",
                 "channels": "Channels",
                 "oauth": "OAuth",
                 }

    def get_template_names(self):
        return [f'bitcaster/settings/{self._section}.html',
                'bitcaster/settings/base.html']

    def get_context_data(self, **kwargs):
        kwargs = super(SettingsView, self).get_context_data(**kwargs)
        kwargs['title'] = self.title_map[self._section]
        return kwargs

    @property
    def _section(self):
        return self.kwargs.get('section', 'main').lower()

    def get_form_class(self):
        """Return the form class to use."""
        return self.form_map[self._section]

    def get_form(self, form_class=None):
        # if form_class is None:
        form_class = self.get_form_class()
        kwargs = self.get_form_kwargs()

        kwargs['initial'] = dict({(f, getattr(config, f, ''))
                                  for f in form_class.declared_fields.keys()})
        return form_class(**kwargs)

    def form_valid(self, form):
        for k, v in form.cleaned_data.items():
            setattr(config, k, v)
        return super().form_valid(form)
