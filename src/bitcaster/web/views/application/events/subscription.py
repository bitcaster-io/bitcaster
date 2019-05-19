from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _, ungettext
from django.views.generic import FormView

from bitcaster import messages
from bitcaster.framework.db.fields import ROLES
from bitcaster.models import Event
from bitcaster.web.forms.subscription import (EventSubscriptionCreateForm,
                                              InviteFormSet,)
from bitcaster.web.views.application.events.event import EventMixin
from bitcaster.web.views.base import (
    BitcasterBaseDeleteView, BitcasterBaseListView, BitcasterBaseToggleView,
    MessageUserMixin,)


class SingleEventMixin(EventMixin):
    def get_context_data(self, **kwargs):
        kwargs['event'] = self.selected_event
        return super().get_context_data(selected_event=self.selected_event,
                                        **kwargs)

    @cached_property
    def selected_event(self):
        return Event.objects.get(application=self.selected_application,
                                 id=self.kwargs['event'])


class EventSubscriptionList(SingleEventMixin, BitcasterBaseListView):
    template_name = 'bitcaster/application/events/subscriptions/list.html'

    title = '%(event)s Subscribers'

    def get_context_data(self, **kwargs):
        # kwargs['event'] = self.selected_event
        return super().get_context_data(**kwargs)


class EventSubscriptionDelete(SingleEventMixin, BitcasterBaseDeleteView):
    pk_url_kwarg = 'subscription'

    def get_queryset(self):
        return self.selected_event.subscriptions.all()


class EventSubscriptionToggle(SingleEventMixin, BitcasterBaseToggleView):
    def get_object(self, queryset=None):
        return self.selected_event.subscriptions.get(id=self.kwargs['subscription'])


class EventSubscriptionCreate(SingleEventMixin, MessageUserMixin, FormView):
    template_name = 'bitcaster/application/events/subscriptions/subscribe.html'
    # title = 'Subscribers'
    form_class = EventSubscriptionCreateForm

    def get_object(self, queryset):
        return self.selected_event

    def get_success_url(self):
        return reverse('app-event-subscriptions',
                       args=[self.selected_organization.slug,
                             self.selected_application.slug,
                             self.selected_event.pk])

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['application'] = self.selected_application
        kwargs['instance'] = self.selected_event
        return kwargs

    def form_valid(self, form):
        existing = []
        channel = form.cleaned_data['channel']
        count = len(form.cleaned_data['members'])
        for user in form.cleaned_data['members']:
            if user.subscriptions.filter(event=self.selected_event):
                existing.append(user.display_name)

            user.subscriptions.create(event=self.selected_event,
                                      trigger_by=self.request.user,
                                      channel=channel)

        self.message_user(ungettext('%s subscription created',
                                    '%s subscriptions created',
                                    count
                                    ) % count)
        if existing:
            self.message_user(ungettext('%s was alredy subscribed',
                                        '%s were alredy subscribed',
                                        len(existing)
                                        ) % ','.join(existing))

        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        kwargs['members_autocomplete_url'] = reverse('org-member-autocomplete',
                                                     args=[self.selected_organization.slug,
                                                           ])
        kwargs['event'] = self.selected_event
        return super().get_context_data(**kwargs)


class EventSubscriptionInvite(SingleEventMixin, MessageUserMixin, FormView):
    template_name = 'bitcaster/application/events/subscriptions/invite.html'
    # title = 'Subscribers'
    form_class = InviteFormSet

    def get_object(self):
        return self.get_queryset().get(pk=self.kwargs['event'])

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['event'] = self.get_object()
        kwargs['requestor'] = self.request.user
        return kwargs

    def form_valid(self, formset):
        formset.instance = self.selected_organization
        for form in formset:
            recipient = form.cleaned_data.get('email', None)
            if self.selected_organization.memberships.filter(email=recipient).exists():
                self.message_user(_('Email %s already exists in this organization' % recipient), messages.WARNING)
            else:
                form.instance.organization = self.selected_organization
                form.instance.event = self.get_object()
                form.instance.role = ROLES.MEMBER
                form.instance.invited_by = self.request.user
                membership = form.save()
                membership.send_email()

        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        kwargs['event'] = self.get_object()
        return super().get_context_data(**kwargs)
