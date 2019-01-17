# -*- coding: utf-8 -*-
import logging

from django import forms
from django.forms import BaseFormSet
from django.forms.models import BaseInlineFormSet, inlineformset_factory
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, ListView, RedirectView
from rest_framework.serializers import Serializer

from bitcaster.db.fields import Role
from bitcaster.models import (AuditEvent, Event, Message,
                              OrganizationMember, Subscription,)
from bitcaster.web.forms.event import EventForm
from bitcaster.web.forms.message import MessageForm
from bitcaster.web.views import (DeleteView, DetailView, FormView,
                                 MessageUserMixin, Organization,
                                 SelectedApplicationMixin, UpdateView,
                                 import_by_name, messages,)
from bitcaster.web.views.organization import OrganizationAuditMixin

logger = logging.getLogger(__name__)


class EventMixin(SelectedApplicationMixin, MessageUserMixin):
    model = Event

    def get_success_url(self):
        if 'save_edit_messages' in self.request.POST:
            return reverse('app-event-messages',
                           args=[self.selected_organization.slug,
                                 self.selected_application.slug,
                                 self.object.pk]
                           )
        else:
            return reverse('app-event-list',
                           args=[self.selected_organization.slug,
                                 self.selected_application.slug])

    def get_queryset(self):
        return self.selected_application.events.all()

    def get_context_data(self, **kwargs):
        kwargs['title'] = self.title
        return super().get_context_data(**kwargs)


class EventFormMixin:
    form_class = EventForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'application': self.selected_application})
        return kwargs


class EventList(EventMixin, ListView):
    template_name = 'bitcaster/event_list.html'
    title = 'Application Events'


class EventCreate(EventMixin, EventFormMixin, CreateView):
    title = 'Create Event'

    def get_context_data(self, **kwargs):
        return super().get_context_data(save_label=_('Create Event'),
                                        mode_create=True,
                                        **kwargs)

    def form_valid(self, form):
        self.message_user(_('Event created'), messages.SUCCESS)
        ret = super().form_valid(form)
        event = self.object
        for i, channel in enumerate(event.channels.all()):
            Message.objects.get_or_create(event=event,
                                          channel=channel,
                                          defaults={
                                              'enabled': True,
                                              'name': f'{event} {channel}',
                                          })
        self.object.messages.exclude(channel__in=self.object.channels.all()).delete()
        return ret


class EventUpdate(EventMixin, EventFormMixin, UpdateView):
    title = 'Edit Event'

    def get_context_data(self, **kwargs):
        return super().get_context_data(save_label=_('Save Event'),
                                        **kwargs)

    def form_valid(self, form):
        self.message_user(_('Event saved'), messages.SUCCESS)
        ret = super().form_valid(form)
        event = self.object
        for i, channel in enumerate(event.channels.all()):
            Message.objects.get_or_create(event=event,
                                          channel=channel,
                                          defaults={
                                              'enabled': True,
                                              'name': f'{event} {channel}',
                                          })
        self.object.messages.exclude(channel__in=self.object.channels.all()).delete()
        return ret


class EventDelete(EventMixin, EventFormMixin, DeleteView):
    title = 'Edit Event'

    def get_context_data(self, **kwargs):
        return super().get_context_data(save_label=_('Save Event'),
                                        **kwargs)


def eventform_factory(event: Event):
    attrs = {}
    for fld in event.arguments['fields']:
        attrs[fld['name']] = import_by_name(fld['type'])()

    return type('AAA', (Serializer,), attrs)()


class EventTest(EventMixin, EventFormMixin, DetailView):
    template_name = 'bitcaster/event_test.html'
    title = 'Test'

    def get_context_data(self, **kwargs):
        event = self.get_object()
        key = self.selected_application.keys.filter(events=event).first()
        if not key:
            key = self.selected_application.keys.create(name=f'Auto created key for {event}')
            key.events.add(event)
            self.message_user('Warning new key has been created', messages.WARNING)

        # key = self.request.user.triggers.filter(application=event.application).first()
        # if not key:
        #     key = self.request.user.triggers.create(application=event.application)
        #
        extra = {'serializer': eventform_factory(event),
                 'key': key,
                 'api_url': self.request.build_absolute_uri(reverse('api:application-event-trigger',
                                                                    args=[event.application.pk, event.pk]))}

        kwargs.update(extra)
        return super().get_context_data(**kwargs)


class EventToggle(EventMixin, EventFormMixin, RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        return self.get_success_url()

    def get(self, request, *args, **kwargs):
        obj = self.selected_application.events.get(id=kwargs['pk'])
        if obj.messages.count() == 0:
            self.message_user(f'No messages configured for this event. '
                              f'Cannot be enabled', messages.ERROR)
        else:
            obj.enabled = not obj.enabled
            if obj.enabled:
                ok = obj.messages.filter(enabled=True).exists()
                if not ok:
                    self.message_user(f'Event cannot be enabled because '
                                      f'all messages are disabled', messages.ERROR)
                    return super().get(request, *args, **kwargs)

                for msg in obj.messages.all():
                    if not msg.body:
                        self.message_user(f'Event cannot be enabled because '
                                          f'message "{msg.name}" does not validate', messages.ERROR)
                        return super().get(request, *args, **kwargs)

                    msg.clean()

            obj.save()
            op = 'enabled' if obj.enabled else 'disabled'
            self.message_user(f'Event {op}')
        return super().get(request, *args, **kwargs)


class MessageInlineFormSet(forms.BaseInlineFormSet):
    pass
    # def clean(self):
    #     forms_to_delete = self.deleted_forms
    #     at_least_one_enabled = False
    #     for form in self.forms:
    #         if form not in forms_to_delete:
    #             print(111, form.instance.channel.handler.validate_message())
    #     return super().clean()


class EventSubscriptions(EventMixin, EventFormMixin, DetailView):
    template_name = 'bitcaster/event_subscriptions.html'
    title = 'Subscribers'

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)


class SubscriptionForm(forms.ModelForm):
    trigger_by = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        self.application = kwargs.pop('application', None)
        self.event = kwargs.pop('event', None)
        self.requestor = kwargs.pop('requestor', None)
        super().__init__(*args, **kwargs)
        self.fields['channel'].queryset = self.event.enabled_channels()

    def clean(self):
        cleaned_data = super().clean()
        cleaned_data['event'] = self.event
        cleaned_data['trigger_by'] = self.requestor
        return cleaned_data

    class Meta:
        model = Subscription
        fields = ('subscriber', 'channel', 'event', 'trigger_by')


class SubscriptionBaseFormSet(BaseInlineFormSet):

    def __init__(self, *args, **kwargs):
        self.event = kwargs.pop('event')
        self.requestor = kwargs.pop('requestor')
        super().__init__(*args, **kwargs)
        self.form_kwargs['event'] = self.event
        self.form_kwargs['requestor'] = self.requestor


SubscriptionFormSet = forms.inlineformset_factory(Event,
                                                  Subscription,
                                                  form=SubscriptionForm,
                                                  formset=SubscriptionBaseFormSet,
                                                  min_num=1,
                                                  extra=0)


class EventSubscriptionsSubscribe(EventMixin, FormView):
    template_name = 'bitcaster/event_subscriptions_subscribe.html'
    title = 'Subscribers'
    form_class = SubscriptionForm

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
        # formset.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        kwargs['event'] = self.get_object()
        return super().get_context_data(**kwargs)


class InviteForm(forms.ModelForm):
    email = forms.EmailField()

    def __init__(self, *args, **kwargs):
        self.application = kwargs.pop('application', None)
        self.event = kwargs.pop('event', None)
        self.requestor = kwargs.pop('requestor', None)
        super().__init__(*args, **kwargs)

    class Meta:
        model = OrganizationMember
        fields = ('email',)


class InviteBaseFormSet(BaseFormSet):

    def __init__(self, *args, **kwargs):
        self.event = kwargs.pop('event')
        self.requestor = kwargs.pop('requestor')
        super().__init__(*args, **kwargs)
        self.form_kwargs['event'] = self.event
        self.form_kwargs['requestor'] = self.requestor


InviteFormSet = forms.inlineformset_factory(Organization,
                                            OrganizationMember,
                                            form=InviteForm,
                                            formset=InviteBaseFormSet,
                                            min_num=1,
                                            extra=0)


class EventSubscriptionsInvite(EventMixin, FormView, OrganizationAuditMixin):
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
            if not self.selected_organization.memberships.filter(email=recipient).exists():
                form.instance.organization = self.selected_organization
                form.instance.event = self.get_object()
                form.instance.role = int(Role.SUBSCRIBER)
                membership = form.save()
                membership.send_email()
                self.audit_log(AuditEvent.MEMBER_INVITE,
                               role=membership.get_role_display(),
                               email=membership.email)

        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        kwargs['event'] = self.get_object()
        return super().get_context_data(**kwargs)


class EventMessages(EventMixin, EventFormMixin, UpdateView):
    template_name = 'bitcaster/event_messages.html'
    title = 'Messages'

    # def get_context_data(self, **kwargs):
    #     return super().get_context_data(**kwargs)

    def get_form_kwargs(self):
        ret = super().get_form_kwargs()
        ret.pop('application')
        return ret

    def get_form_class(self):
        form = type('MessageForm', (MessageForm,), dict(event=self.get_object()))
        return inlineformset_factory(Event, Message, form,
                                     formset=MessageInlineFormSet,
                                     extra=0)

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        formset = form_class(**self.get_form_kwargs())
        event = self.get_object()
        for form in formset:
            form.event = event
            form.has_subject = form.instance.channel.handler.message_class.has_subject
        # frm.instance = self.get_object()

        return formset

    # def form_valid(self, form):
    #     return super().form_valid(form)
    #
    # def post(self, request, *args, **kwargs):
    #     return super().post(request, *args, **kwargs)
    #
    # def form_invalid(self, form):
    #     return super().form_invalid(form)
