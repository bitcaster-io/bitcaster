# -*- coding: utf-8 -*-
import logging

from django import forms
from django.forms.models import BaseModelFormSet
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import ugettext as _
from django.views.generic import CreateView, ListView, RedirectView
from formtools.wizard.views import SessionWizardView

from bitcaster.models import Event, Message
from bitcaster.web.forms.event import EventForm
from bitcaster.web.forms.message import MessageCreateForm
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


MessageFormSet = forms.modelformset_factory(Message,
                                            form=MessageCreateForm,
                                            extra=0,
                                            # max_num=10,
                                            can_delete=True)


class EventCreateWizard(EventMixin, MessageUserMixin, SessionWizardView):
    form_list = [("a", EventForm),
                 ("b", MessageFormSet),
                 ]
    TEMPLATES = {"a": "bitcaster/app_event_wizard1.html",
                 "b": "bitcaster/app_event_wizard2.html",
                 }

    # def get_form_initial(self, step):
    #     ret = super().get_form_initial(step)
    #     ret['application'] = self.selected_application
    #     return ret

    def get_object(self):
        return Event.objects.get(pk=self.kwargs['pk'])

    def get_form_kwargs(self, step=None):
        kwargs = super().get_form_kwargs(step)
        if step == 'a':
            if self.kwargs.get('pk', None):
                kwargs['instance'] = self.get_object()
            kwargs['application'] = self.selected_application
        else:
            if self.kwargs.get('pk', None):
                event = self.get_object()
                kwargs['queryset'] = event.messages.all()
            else:
                kwargs['queryset'] = Message.objects.none()

        return kwargs

    def get_form(self, step=None, data=None, files=None):
        if step == 'b':
            def cb(field, **kw):
                if field.name == 'channels':
                    return forms.ModelMultipleChoiceField(queryset=self.selected_application.channels,
                                                          **kw)
                return field.formfield(**kw)

            fs = forms.inlineformset_factory(Event,
                                             Message,
                                             form=MessageCreateForm,
                                             formset=BaseModelFormSet,
                                             extra=0,
                                             can_delete=False,
                                             formfield_callback=cb,
                                             )
            kwargs = self.get_form_kwargs(step)
            kwargs.update({
                'data': data,
                'files': files,
                'prefix': self.get_form_prefix(step, fs),
                'initial': self.get_form_initial(step),
            })
            return fs(**kwargs)
        else:
            ret = super().get_form(step, data, files)

        return ret

    def get_context_data(self, form, **kwargs):
        context = super().get_context_data(form=form, **kwargs)
        if self.steps.current == 'a':
            pass
        elif self.steps.current == 'b':
            pass
        else:
            pass
        return context

    def get_template_names(self):
        return [self.TEMPLATES[self.steps.current]]

    def done(self, form_list, **kwargs):
        event_data = self.storage.get_step_data('a')
        messages_data = self.storage.get_step_data('b')
        try:
            if self.kwargs.get('pk'):
                form1 = self.get_form('a', event_data)
                form1.is_valid()
                event = form1.save()

                fs = self.get_form('b', messages_data)
                fs.instance = event
                fs.is_valid()
                fs.save()
                self.message_user(_('Event updated'))

            else:
                form1 = self.get_form('a', event_data)
                form1.is_valid()
                event = form1.save()

                fs = self.get_form('b', messages_data)
                for i in range(0, fs.total_form_count()):
                    form = fs.forms[i]
                    form.instance.event = event
                fs.is_valid()
                fs.save()
                self.message_user(_('Event created'))
        except Exception as e:
            logger.exception(e)
            raise

        return HttpResponseRedirect(reverse("app-event-list",
                                            args=[self.selected_organization.slug,
                                                  self.selected_application.slug]))
