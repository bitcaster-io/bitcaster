# -*- coding: utf-8 -*-
import logging

from django import forms
from django.forms.models import BaseInlineFormSet, inlineformset_factory
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import ugettext as _
from django.views.generic import CreateView, ListView, RedirectView
from rest_framework.serializers import Serializer

from bitcaster.models import Event, Message, Subscription
from bitcaster.models.subscription import SubscriptionStatus
from bitcaster.web.forms.event import EventForm
from bitcaster.web.forms.message import MessageForm
from bitcaster.web.views import (DeleteView, DetailView, FormView,
                                 MessageUserMixin, SelectedApplicationMixin,
                                 UpdateView, import_by_name, messages,)

logger = logging.getLogger(__name__)


class EventMixin(SelectedApplicationMixin, MessageUserMixin):
    model = Event

    def get_success_url(self):
        if 'save_edit_messages' in self.request.POST:
            return reverse("app-event-messages",
                           args=[self.selected_organization.slug,
                                 self.selected_application.slug,
                                 self.object.pk]
                           )
        else:
            return reverse("app-event-list",
                           args=[self.selected_organization.slug,
                                 self.selected_application.slug])

    def get_queryset(self):
        return self.selected_application.events.all()

    def get_context_data(self, **kwargs):
        kwargs["title"] = self.title
        return super().get_context_data(**kwargs)


class EventFormMixin:
    form_class = EventForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({"application": self.selected_application})
        return kwargs


class EventList(EventMixin, ListView):
    template_name = "bitcaster/event_list.html"
    title = 'Application Events'


class EventCreate(EventMixin, EventFormMixin, CreateView):
    title = "Create Event"

    def get_context_data(self, **kwargs):
        return super().get_context_data(save_label=_("Create Event"),
                                        mode_create=True,
                                        **kwargs)

    def form_valid(self, form):
        self.message_user(_("Event created"), messages.SUCCESS)
        ret = super().form_valid(form)
        event = self.object
        for i, channel in enumerate(event.channels.all()):
            Message.objects.get_or_create(event=event,
                                          channel=channel,
                                          defaults={
                                              "name": f"{event} {channel}",
                                          })
        self.object.messages.exclude(channel__in=self.object.channels.all()).delete()
        return ret


class EventUpdate(EventMixin, EventFormMixin, UpdateView):
    title = "Edit Event"

    def get_context_data(self, **kwargs):
        return super().get_context_data(save_label=_("Save Event"),
                                        **kwargs)

    def form_valid(self, form):
        self.message_user(_("Event saved"), messages.SUCCESS)
        ret = super().form_valid(form)
        event = self.object
        for i, channel in enumerate(event.channels.all()):
            Message.objects.get_or_create(event=event,
                                          channel=channel,
                                          enabled=False,
                                          defaults={
                                              "name": f"{event} {channel}",
                                          })
        self.object.messages.exclude(channel__in=self.object.channels.all()).delete()
        return ret


class EventDelete(EventMixin, EventFormMixin, DeleteView):
    title = "Edit Event"

    def get_context_data(self, **kwargs):
        return super().get_context_data(save_label=_("Save Event"),
                                        **kwargs)


def eventform_factory(event: Event):
    attrs = {}
    for fld in event.arguments['fields']:
        attrs[fld['name']] = import_by_name(fld['type'])()

    return type("AAA", (Serializer,), attrs)()


class EventTest(EventMixin, EventFormMixin, DetailView):
    template_name = 'bitcaster/event_test.html'
    title = 'Test'

    def get_context_data(self, **kwargs):
        event = self.get_object()
        key = self.request.user.triggers.filter(application=event.application).first()
        if not key:
            key = self.request.user.triggers.create(application=event.application)

        extra = {'serializer': eventform_factory(event),
                 'user_token': key,
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
            op = "enabled" if obj.enabled else "disabled"
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

    def __init__(self, *args, **kwargs):
        self.application = kwargs.pop('application', None)
        self.event = kwargs.pop('event', None)
        super().__init__(*args, **kwargs)
        self.fields['channel'].queryset = self.event.channels

    def clean(self):
        cleaned_data = super().clean()
        cleaned_data['event'] = self.event
        return cleaned_data

    class Meta:
        model = Subscription
        fields = ('subscriber', 'channel', 'event', 'locked')


class SubscriptionBaseFormSet(BaseInlineFormSet):

    def __init__(self, *args, **kwargs):
        self.event = kwargs.pop('event')
        super().__init__(*args, **kwargs)
        self.form_kwargs['event'] = self.event


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

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['event'] = self.get_object()
        return kwargs

    def form_valid(self, form):
        for frm in form:
            data = frm.cleaned_data.copy()
            data['event'] = self.get_object()
            data.pop('DELETE')
            Subscription.objects.create(status=SubscriptionStatus.MANAGED,
                                        trigger_by=self.request.user,
                                        **data)

        return HttpResponseRedirect(self.get_success_url())

    def get_form_class(self):
        return SubscriptionFormSet

    def get_context_data(self, **kwargs):
        kwargs['event'] = self.get_object()
        return super().get_context_data(**kwargs)


#
#
# def messageformset_factory(application):
#     FormSet = modelformset_factory(Message,
#                                    form=MessageForm,
#                                    # formset=MessageInlineFormSet,
#                                    extra=0)
#     # FormSet.fk = _get_foreign_key(Event, Message)
#     FormSet.model = Message
#     return FormSet


class EventMessages(EventMixin, EventFormMixin, UpdateView):
    template_name = 'bitcaster/event_messages.html'
    title = 'Messages'

    def get_context_data(self, **kwargs):
        # kwargs['formset'] =
        # kwargs['formset'] = inlineformset_factory()
        return super().get_context_data(**kwargs)

    def get_form_kwargs(self):
        ret = super().get_form_kwargs()
        ret.pop('application')
        return ret

    def get_form_class(self):
        form = type("MessageForm", (MessageForm,), dict(event=self.get_object()))
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
#
# class EventCreateWizard(EventMixin, MessageUserMixin, SessionWizardView):
#     form_list = [("a", EventForm),
#                  ("b", MessageFormSet),
#                  ]
#     TEMPLATES = {"a": "bitcaster/app_event_wizard1.html",
#                  "b": "bitcaster/app_event_wizard2.html",
#                  }
#
#     # def get_form_initial(self, step):
#     #     ret = super().get_form_initial(step)
#     #     ret['application'] = self.selected_application
#     #     return ret
#
#     def get_object(self):
#         return Event.objects.get(pk=self.kwargs['pk'])
#
#     def get_form_kwargs(self, step=None):
#         kwargs = super().get_form_kwargs(step)
#         if step == 'a':
#             if self.kwargs.get('pk', None):
#                 kwargs['instance'] = self.get_object()
#             kwargs['application'] = self.selected_application
#         else:
#             if self.kwargs.get('pk', None):
#                 event = self.get_object()
#                 kwargs['queryset'] = event.messages.all()
#             else:
#                 kwargs['queryset'] = Message.objects.none()
#
#         return kwargs
#
#     def get_form(self, step=None, data=None, files=None):
#         if step == 'b':
#             def cb(field, **kw):
#                 if field.name == 'channels':
#                     return forms.ModelMultipleChoiceField(queryset=self.selected_application.channels,
#                                                           **kw)
#                 return field.formfield(**kw)
#
#             fs = forms.modelformset_factory(Message,
#                                             form=MessageCreateForm,
#                                             formset=BaseModelFormSet,
#                                             extra=0,
#                                             can_delete=False,
#                                             formfield_callback=cb,
#                                             )
#             kwargs = self.get_form_kwargs(step)
#             kwargs.update({
#                 'data': data,
#                 'files': files,
#                 'prefix': self.get_form_prefix(step, fs),
#                 'initial': self.get_form_initial(step),
#             })
#             return fs(**kwargs)
#         else:
#             ret = super().get_form(step, data, files)
#
#         return ret
#
#     def get_context_data(self, form, **kwargs):
#         context = super().get_context_data(form=form, **kwargs)
#         if self.steps.current == 'a':
#             pass
#         elif self.steps.current == 'b':
#             pass
#         else:
#             pass
#         return context
#
#     def get_template_names(self):
#         return [self.TEMPLATES[self.steps.current]]
#
#     def done(self, form_list, **kwargs):
#         event_data = self.storage.get_step_data('a')
#         messages_data = self.storage.get_step_data('b')
#         try:
#             if self.kwargs.get('pk'):
#                 form1 = self.get_form('a', event_data)
#                 form1.is_valid()
#                 event = form1.save()
#
#                 fs = self.get_form('b', messages_data)
#                 fs.instance = event
#                 fs.is_valid()
#                 fs.save()
#                 self.message_user(_('Event updated'))
#
#             else:
#                 form1 = self.get_form('a', event_data)
#                 form1.is_valid()
#                 event = form1.save()
#
#                 fs = self.get_form('b', messages_data)
#                 for i in range(0, fs.total_form_count()):
#                     form = fs.forms[i]
#                     form.instance.event = event
#                 fs.is_valid()
#                 fs.save()
#                 self.message_user(_('Event created'))
#         except Exception as e:
#             logger.exception(e)
#             raise
#
#         return HttpResponseRedirect(reverse("app-event-list",
#                                             args=[self.selected_organization.slug,
#                                                   self.selected_application.slug]))
