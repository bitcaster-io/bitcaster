import logging

from django.db.models import Q
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import RedirectView
from rest_framework.serializers import Serializer

from bitcaster.models import AuditEvent, Event, Message
from bitcaster.utils.language import parse_bool
from bitcaster.web import messages
from bitcaster.web.forms import EventForm
from bitcaster.web.views.application.mixins import SelectedApplicationMixin
from bitcaster.web.views.base import (
    BitcasterBaseCreateView, BitcasterBaseDeleteView, BitcasterBaseDetailView,
    BitcasterBaseListView, BitcasterBaseUpdateView, MessageUserMixin,)
from bitcaster.web.views.mixins import FilterQuerysetMixin, LogAuditMixin

logger = logging.getLogger(__name__)


class EventMixin(LogAuditMixin, SelectedApplicationMixin):
    model = Event

    def get_success_url(self):
        if 'save_edit_messages' in self.request.POST:
            return reverse('app-event-messages',
                           args=[self.selected_organization.slug,
                                 self.selected_application.slug,
                                 self.object.pk]
                           )
        else:
            return self.request.META.get('HTTP_REFERER',
                                         reverse('app-events',
                                                 args=[self.selected_organization.slug,
                                                       self.selected_application.slug])
                                         )

    def get_queryset(self):
        return self.selected_application.events.all()


class EventFormMixin:
    form_class = EventForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'application': self.selected_application})
        return kwargs


class EventList(EventMixin, FilterQuerysetMixin, BitcasterBaseListView):
    template_name = 'bitcaster/application/events/list.html'
    search_fields = ['name__istartswith']
    filter_fieldmap = {
        # Translators: UserNotificationLogView.filter_fieldmap
        _('channel'): 'channel__name__iexact',
        _('occurence'): 'occurence_id',
        _('enabled'): '_parse_bool',
        _('debug'): lambda s, f, v: (s.kwargs.__setitem__('development_mode', parse_bool(v))),
    }

    def get_queryset(self):
        return self.filter_queryset(super().get_queryset())


class EventCreate(EventMixin, EventFormMixin, BitcasterBaseCreateView):
    # title = 'Create Event'
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
                                          })
        self.object.messages.exclude(channel__in=self.object.channels.all()).delete()
        self.audit(self.object, AuditEvent.EVENT_CREATED)
        return ret


class EventUpdate(EventMixin, EventFormMixin, BitcasterBaseUpdateView):
    # title = 'Edit Event'
    template_name = 'bitcaster/application/events/form.html'

    def get_context_data(self, **kwargs):
        return super().get_context_data(save_label=_('Save Event'),
                                        **kwargs)

    def form_valid(self, form):
        ret = super().form_valid(form)
        event = self.object
        for channel in event.channels.all():
            Message.objects.update_or_create(event=event,
                                             channel=channel,
                                             application=event.application,
                                             defaults={
                                                 'enabled': True,
                                             })
        self.object.messages.exclude(channel__in=self.object.channels.all()).delete()
        self.audit(self.object, AuditEvent.CHANNEL_UPDATED)
        self.message_user(_('Event updated'))
        return ret


class EventDelete(EventMixin, EventFormMixin, BitcasterBaseDeleteView):
    # title = 'Delete Event'
    def get_success_url(self):
        return reverse('app-events',
                       args=[self.selected_organization.slug,
                             self.selected_application.slug])

    def get_context_data(self, **kwargs):
        return super().get_context_data(save_label=_('Save Event'),
                                        **kwargs)

    def delete(self, request, *args, **kwargs):
        ret = super().delete(request, *args, **kwargs)
        self.audit(self.object, AuditEvent.EVENT_DELETED)
        return ret


def eventform_factory(event: Event):
    attrs = {}
    # if event.arguments:
    #     for fld in event.arguments['fields']:
    #         attrs[fld['name']] = import_by_name(fld['type'])()

    return type('AAA', (Serializer,), attrs)()


class EventBee(EventMixin, EventFormMixin, BitcasterBaseDetailView):
    template_name = 'bitcaster/application/events/links.html'
    title = 'Event endpoints'

    def get_context_data(self, **kwargs):
        event = self.get_object()
        key, is_new = event.get_or_create_key()
        if is_new:
            self.message_user('Warning new key has been created', messages.WARNING)

        extra = {'serializer': eventform_factory(event),
                 'key': key,
                 'api_url': event.get_api_url(),
                 'short_api_url': event.get_short_api_url(key.token),
                 'batch_api_url': event.get_batch_url()
                 }

        kwargs.update(extra)
        return super().get_context_data(**kwargs)


class EventBatch(EventMixin, EventFormMixin, BitcasterBaseDetailView):
    template_name = 'bitcaster/application/events/batch.html'
    title = 'Batch Event'

    def get_context_data(self, **kwargs):
        event = self.get_object()
        key, is_new = event.get_or_create_key()
        if is_new:
            self.message_user('Warning new key has been created', messages.WARNING)

        extra = {'serializer': eventform_factory(event),
                 'key': key,
                 'api_url': event.get_batch_url(),
                 }

        kwargs.update(extra)
        return super().get_context_data(**kwargs)


class EventTest(EventMixin, EventFormMixin, BitcasterBaseDetailView):
    template_name = 'bitcaster/application/events/test.html'
    title = 'Test Event'

    def get_context_data(self, **kwargs):
        event = self.get_object()
        key, is_new = event.get_or_create_key()
        if is_new:
            self.message_user('Warning new key has been created', messages.WARNING)

        extra = {'serializer': eventform_factory(event),
                 'key': key,
                 'api_url': event.get_api_url(),
                 'api_short_url': event.get_short_api_url(key.token)
                 }

        kwargs.update(extra)
        return super().get_context_data(**kwargs)


class EventDeveloperModeToggle(EventMixin, LogAuditMixin, EventFormMixin, MessageUserMixin, RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        return self.request.META.get('HTTP_REFERER', super().get_success_url())

    def get(self, request, *args, **kwargs):
        obj = self.selected_application.events.get(id=kwargs['pk'])
        obj.development_mode = not obj.development_mode
        obj.save()
        # op = 'enabled' if obj.development_mode else 'disabled'
        # self.message_user(f'Event development mode {op}')
        if obj.development_mode:
            self.message_user(_('Event debug mode enabled'))
            self.audit(obj, AuditEvent.EVENT_DEV_MODE_ON)
        else:
            self.message_user(_('Event debug mode disabled'))
            self.audit(obj, AuditEvent.EVENT_DEV_MODE_OFF)
        return super().get(request, *args, **kwargs)


class EventToggle(EventMixin, LogAuditMixin, EventFormMixin, MessageUserMixin, RedirectView):
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
                for msg in obj.messages.all():
                    if not msg.body:
                        self.message_user(_('Event cannot be enabled because '
                                            "'%s' message does not validate"
                                            % msg.channel.name), messages.ERROR)
                        return super().get(request, *args, **kwargs)

                    msg.clean()

            obj.save()
            if obj.enabled:
                self.message_user(_('Event enabled'))
                self.audit(obj, AuditEvent.EVENT_ENABLED)
            else:
                self.message_user(_('Event disabled'))
                self.audit(obj, AuditEvent.EVENT_DISABLED)
        return super().get(request, *args, **kwargs)


class EventKeys(EventMixin, EventFormMixin, BitcasterBaseUpdateView):
    template_name = 'bitcaster/application/events/keys.html'
    title = 'Keys'

    def get_context_data(self, **kwargs):
        kwargs['keys'] = self.selected_application.keys.filter(Q(events=self.object,
                                                                 all_events=True))
        return super().get_context_data(**kwargs)
