# -*- coding: utf-8 -*-
import logging

from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import ugettext as _
from django.views.generic import CreateView, ListView, RedirectView
from formtools.wizard.views import SessionWizardView

from bitcaster.models import Event, Message
from bitcaster.web.forms.event import (EventCreateSelectChannel,
                                       EventCreateSetupMessage, EventForm,)
from bitcaster.web.views import (DeleteView, MessageUserMixin,
                                 SelectedApplicationMixin, UpdateView, messages,)

logger = logging.getLogger(__name__)


class EventMixin(SelectedApplicationMixin, MessageUserMixin):
    model = Event

    def get_success_url(self):
        return reverse("app-event-list",
                       args=[self.selected_organization.slug,
                             self.selected_application.slug])

    def get_queryset(self):
        return self.selected_application.events.all()


class EventFormMixin:
    form_class = EventForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({"application": self.selected_application})
        return kwargs

    def get_context_data(self, **kwargs):
        kwargs["title"] = self.title
        return super().get_context_data(**kwargs)


class EventList(EventMixin, ListView):
    template_name = "bitcaster/event_list.html"


class EventCreate(EventMixin, EventFormMixin, CreateView):
    title = "Create Event"

    def get_context_data(self, **kwargs):
        return super().get_context_data(save_label=_("Create Event"),
                                        **kwargs)


class EventUpdate(EventMixin, EventFormMixin, UpdateView):
    title = "Edit Event"

    def get_context_data(self, **kwargs):
        return super().get_context_data(save_label=_("Save Event"),
                                        **kwargs)

    def form_valid(self, form):
        self.message_user(_("Event saved"), messages.SUCCESS)
        return super().form_valid(form)


class EventDelete(EventMixin, EventFormMixin, DeleteView):
    title = "Edit Event"

    def get_context_data(self, **kwargs):
        return super().get_context_data(save_label=_("Save Event"),
                                        **kwargs)


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
            obj.save()
            op = "enabled" if obj.enabled else "disabled"
            self.message_user(f'Event {op}')
        return super().get(request, *args, **kwargs)


class EventCreateWizard(EventMixin, MessageUserMixin, SessionWizardView):
    form_list = [("a", EventForm),
                 ("b", EventCreateSelectChannel),
                 ("c", EventCreateSetupMessage),
                 # todo: add summary screen
                 ]
    TEMPLATES = {"a": "bitcaster/app_event_wizard1.html",
                 "b": "bitcaster/app_event_wizard2.html",
                 "c": "bitcaster/app_event_wizard3.html",
                 }

    def get_form_initial(self, step):
        return super().get_form_initial(step)

    def process_step(self, form):
        ret = super().process_step(form)
        return ret

    def get_form_kwargs(self, step=None):
        kwargs = {'application': self.selected_application}
        if step == "c":
            data = self.storage.get_step_data('b')
            kwargs["channels"] = data.getlist('b-channels')
            return kwargs
        return kwargs

    def get_context_data(self, form, **kwargs):
        context = super().get_context_data(form=form, **kwargs)
        if self.steps.current == 'a':
            pass
        elif self.steps.current == 'b':
            pass
        else:
            pass
        return context

    def post(self, *args, **kwargs):
        return super().post(*args, **kwargs)

    def get_template_names(self):
        return [self.TEMPLATES[self.steps.current]]

    def get_extra_instance_kwargs(self):
        return {}

    def done(self, form_list, **kwargs):
        event_data = self.get_cleaned_data_for_step('a')
        channels_data = self.get_cleaned_data_for_step('b')
        message_data = self.get_cleaned_data_for_step('c')
        try:
            event = Event.objects.create(application=self.selected_application,
                                         **dict(event_data))
            msg = Message.objects.create(event=event,
                                   application=self.selected_application,
                                   **dict(message_data))
            msg.channels.set(channels_data['channels'])
            self.message_user(_('Event created'))
        except Exception as e:
            logger.exception(e)
            raise

        return HttpResponseRedirect(reverse("app-event-list",
                                            args=[self.selected_organization.slug,
                                                  self.selected_application.slug]))
