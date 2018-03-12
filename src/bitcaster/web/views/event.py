# -*- coding: utf-8 -*-
import logging

from django.urls import reverse
from django.views.generic import ListView, CreateView, RedirectView
from django.utils.translation import ugettext as _
from bitcaster.models import Event
from bitcaster.web.forms import EventForm
from bitcaster.web.views import SelectedApplicationMixin, UpdateView, DeleteView, MessageUserMixin

logger = logging.getLogger(__name__)


class EventMixin(SelectedApplicationMixin, MessageUserMixin):
    model = Event

    def get_success_url(self):
        return reverse("app-event-list",
                       args=[self.selected_organization.slug,
                             self.selected_application.slug])

    def get_queryset(self):
        return self.selected_application.events.all()


class EventList(EventMixin, ListView):
    template_name = "bitcaster/event_list.html"


class EventFormMixin:
    form_class = EventForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({"application": self.selected_application})
        return kwargs

    def get_context_data(self, **kwargs):
        kwargs["title"] = self.title
        return super().get_context_data(**kwargs)


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
        obj.enabled = not obj.enabled
        obj.save()
        op = "enabled" if obj.enabled else "disabled"
        self.message_user(f'Event {op}')
        return super().get(request, *args, **kwargs)
