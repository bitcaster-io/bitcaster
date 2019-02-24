from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView, RedirectView

from bitcaster import messages
from bitcaster.db.fields import Role
from bitcaster.middleware.exception import RedirectToRefererResponse
from bitcaster.models import AuditEvent
from bitcaster.web.forms.subscription import (EventSubscriptionForm,
                                              InviteFormSet,
                                              SubscriptionFormSet,)
from bitcaster.web.views.base import (BitcasterBaseDeleteView,
                                      BitcasterBaseListView, MessageUserMixin,)
from bitcaster.web.views.event import SingleEventMixin
from bitcaster.web.views.organization import OrganizationAuditMixin


class EventSubscriptionList(SingleEventMixin, BitcasterBaseListView):
    template_name = 'bitcaster/application/events/subscriptions/list.html'
    title = 'Subscribers'

    def get_context_data(self, **kwargs):
        kwargs['pending'] = self.selected_organization.memberships.filter(event=self.selected_event)
        return super().get_context_data(**kwargs)


class EventSubscriptionDelete(SingleEventMixin, BitcasterBaseDeleteView):
    template_name = 'bitcaster/application/events/subscriptions/confirm_delete.html'

    def get_queryset(self):
        return self.selected_application.subscriptions.all()


class EventSubscriptionToggle(SingleEventMixin, MessageUserMixin, RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        return reverse('app-event-subscriptions',
                       args=[self.selected_organization.slug,
                             self.selected_application.slug,
                             self.selected_event.pk])

    def get(self, request, *args, **kwargs):
        obj = self.selected_event.subscriptions.get(id=kwargs['subscription'])
        obj.active = not obj.active
        obj.save()
        self.message_user(f'Subscription {obj} updated')
        return RedirectToRefererResponse(request)


class EventSubscriptionCreate(SingleEventMixin, FormView):
    template_name = 'bitcaster/application/events/subscriptions/subscribe.html'
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


class EventSubscriptionInvite(SingleEventMixin, MessageUserMixin, FormView, OrganizationAuditMixin):
    template_name = 'bitcaster/application/events/subscriptions/invite.html'
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
