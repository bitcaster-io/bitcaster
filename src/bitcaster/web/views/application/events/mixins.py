from django.urls import reverse
from django.utils.functional import cached_property

from bitcaster.models import Event, Message
from bitcaster.web.forms import EventForm, MessageForm
from bitcaster.web.views.application.mixins import SelectedApplicationMixin
from bitcaster.web.views.mixins import MessageUserMixin


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
            return reverse('app-events',
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


class SingleEventMixin(EventMixin):
    def get_context_data(self, **kwargs):
        kwargs['event'] = self.selected_event
        return super().get_context_data(selected_event=self.selected_event,
                                        **kwargs)

    @cached_property
    def selected_event(self):
        return Event.objects.get(application=self.selected_application,
                                 id=self.kwargs['event'])


class MessageMixin(SelectedApplicationMixin, MessageUserMixin):
    model = Message

    def get_success_url(self):
        return reverse('app-messages',
                       args=[self.selected_organization.slug,
                             self.selected_application.slug])

    def get_queryset(self):
        return self.selected_application.messages.all()


class MessageFormMixin:
    form_class = MessageForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'application': self.selected_application})
        return kwargs

    def get_context_data(self, **kwargs):
        kwargs['title'] = self.title
        return super().get_context_data(**kwargs)
