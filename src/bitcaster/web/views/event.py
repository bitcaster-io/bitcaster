# -*- coding: utf-8 -*-
import logging

from django import forms
from django.forms.models import inlineformset_factory
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django.views.generic import RedirectView
from rest_framework.serializers import Serializer
from strategy_field.utils import import_by_name

from bitcaster import messages
from bitcaster.models import Event, Message
from bitcaster.web.forms import EventForm, MessageForm

from .base import (BitcasterBaseCreateView, BitcasterBaseDeleteView,
                   BitcasterBaseDetailView, BitcasterBaseListView,
                   BitcasterBaseUpdateView, MessageUserMixin,
                   SelectedApplicationMixin,)

logger = logging.getLogger(__name__)


class EventMixin(SelectedApplicationMixin):
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


class SingleEventMixin(EventMixin):
    def get_context_data(self, **kwargs):
        kwargs['event'] = self.selected_event
        return super().get_context_data(selected_event=self.selected_event,
                                        **kwargs)

    @cached_property
    def selected_event(self):
        return Event.objects.get(application=self.selected_application,
                                 id=self.kwargs['event'])


class EventFormMixin:
    form_class = EventForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'application': self.selected_application})
        return kwargs


class EventList(EventMixin, BitcasterBaseListView):
    template_name = 'bitcaster/application/events/list.html'
    title = 'Application Events'


class EventCreate(EventMixin, EventFormMixin, BitcasterBaseCreateView):
    title = 'Create Event'
    template_name = 'bitcaster/application/events/form.html'

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


class EventUpdate(EventMixin, EventFormMixin, BitcasterBaseUpdateView):
    title = 'Edit Event'
    template_name = 'bitcaster/application/events/form.html'

    def get_context_data(self, **kwargs):
        return super().get_context_data(save_label=_('Save Event'),
                                        **kwargs)

    def form_valid(self, form):
        self.message_user(_('Event saved'), messages.SUCCESS)
        ret = super().form_valid(form)
        event = self.object
        for i, channel in enumerate(event.channels.all()):
            Message.objects.update_or_create(event=event,
                                             channel=channel,
                                             defaults={
                                                 'enabled': True,
                                                 'name': f'{event} {channel}',
                                             })
        self.object.messages.exclude(channel__in=self.object.channels.all()).delete()
        return ret


class EventDelete(EventMixin, EventFormMixin, BitcasterBaseDeleteView):
    title = 'Delete Event'
    template_name = 'bitcaster/application/events/confirm_delete.html'

    def get_context_data(self, **kwargs):
        return super().get_context_data(save_label=_('Save Event'),
                                        **kwargs)


def eventform_factory(event: Event):
    attrs = {}
    if event.arguments:
        for fld in event.arguments['fields']:
            attrs[fld['name']] = import_by_name(fld['type'])()

    return type('AAA', (Serializer,), attrs)()


class EventTest(EventMixin, EventFormMixin, BitcasterBaseDetailView):
    template_name = 'bitcaster/application/events/test.html'
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


class EventToggle(EventMixin, EventFormMixin, MessageUserMixin, RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        return self.get_success_url()

    def get(self, request, *args, **kwargs):
        obj = self.selected_application.events.get(id=kwargs['pk'])
        if not obj.messages.exists():
            self.message_user(f'No messages configured for this event. '
                              f'Cannot be enabled', messages.ERROR)
        elif not obj.messages.filter(enabled=True):
            self.message_user(f'No messages enabled for this event. '
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


class EventKeys(EventMixin, EventFormMixin, BitcasterBaseUpdateView):
    template_name = 'bitcaster/application/events/keys.html'
    title = 'Keys'


class EventMessages(EventMixin, EventFormMixin, BitcasterBaseUpdateView):
    template_name = 'bitcaster/application/events/messages.html'
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

    def form_valid(self, form):
        self.message_user('Saved')
        return super().form_valid(form)

    #
    # def post(self, request, *args, **kwargs):
    #     return super().post(request, *args, **kwargs)
    #
    def form_invalid(self, form):
        self.message_user('Invalid', messages.ERROR)
        return super().form_invalid(form)
