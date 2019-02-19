from django.http import HttpResponseRedirect
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, FormView

from bitcaster import messages
from bitcaster.db.fields import Role
from bitcaster.models import AuditEvent
from bitcaster.web.forms.subscription import (EventSubscriptionForm,
                                              InviteFormSet,
                                              SubscriptionFormSet,)
from bitcaster.web.views import MessageUserMixin
from bitcaster.web.views.event import EventFormMixin, EventMixin
from bitcaster.web.views.organization import OrganizationAuditMixin


class EventSubscriptions(EventMixin, EventFormMixin, DetailView):
    template_name = 'bitcaster/event_subscriptions.html'
    title = 'Subscribers'

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)


class EventSubscriptionsSubscribe(EventMixin, FormView):
    template_name = 'bitcaster/event_subscriptions_subscribe.html'
    title = 'Subscribers'
    form_class = EventSubscriptionForm

    def get_object(self):
        return self.get_queryset().get(pk=self.kwargs['pk'])

    def get_form_class(self):
        return SubscriptionFormSet

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['event'] = self.get_object()
        kwargs['requestor'] = self.request.user
        return kwargs

    def form_valid(self, formset):
        formset.instance = self.get_object()
        formset.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        kwargs['event'] = self.get_object()
        return super().get_context_data(**kwargs)


class EventSubscriptionsInvite(EventMixin, MessageUserMixin, FormView, OrganizationAuditMixin):
    template_name = 'bitcaster/event_subscriptions_invite.html'
    title = 'Subscribers'
    form_class = InviteFormSet

    def get_object(self):
        return self.get_queryset().get(pk=self.kwargs['pk'])

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
                form.instance.role = int(Role.SUBSCRIBER)
                form.instance.invited_by = self.request.user
                membership = form.save()
                membership.send_email()
                self.audit_log(AuditEvent.MEMBER_INVITE,
                               role=membership.get_role_display(),
                               email=membership.email)

        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        kwargs['event'] = self.get_object()
        return super().get_context_data(**kwargs)
